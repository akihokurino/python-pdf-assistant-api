import uuid
from datetime import datetime, timezone
from typing import Final, final, List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from adapter.adapter import (
    StorageAdapter,
    DocumentRepository,
    TaskQueueAdapter,
    AssistantRepository,
    OpenAIAdapter,
    AssistantFSRepository,
    MessageFSRepository,
)
from config.envs import DEFAULT_BUCKET_NAME
from di.di import AppContainer
from handler.response import (
    PreSignUploadResp,
    PreSignGetResp,
    DocumentResp,
    EmptyResp,
    DocumentWithUserAndAssistantResp,
    MessageResp,
)
from handler.util import extract_gs_key
from model.document import Document, DocumentId, Status
from model.error import AppError, ErrorKind
from model.user import UserId

router: Final[APIRouter] = APIRouter()


@router.get("/documents/{document_id}")
@inject
async def _get_document(
        document_id: DocumentId,
        document_repository: DocumentRepository = Depends(
            Provide[AppContainer.document_repository]
        ),
) -> DocumentWithUserAndAssistantResp:
    result = await document_repository.get_with_user_and_assistant(document_id)
    if not result:
        raise AppError(
            ErrorKind.NOT_FOUND, f"ドキュメントが見つかりません: {document_id}"
        )

    return DocumentWithUserAndAssistantResp.from_model(result[1], result[0], result[2])


@router.post("/documents/pre_signed_upload_url")
@inject
async def _pre_signed_upload_url(
        request: Request,
        storage_adapter: StorageAdapter = Depends(Provide[AppContainer.storage_adapter]),
) -> PreSignUploadResp:
    uid: Final[UserId] = request.state.uid
    key = f"documents/{uid}/{uuid.uuid4()}.pdf"
    url = storage_adapter.gen_pre_signed_upload_url(key)

    return PreSignUploadResp(url=url, key=key)


@final
class _PreSignedGetUrlPayload(BaseModel):
    gs_url: str


@router.post("/documents/pre_signed_get_url")
@inject
async def _pre_signed_get_url(
        payload: _PreSignedGetUrlPayload,
        storage_adapter: StorageAdapter = Depends(Provide[AppContainer.storage_adapter]),
) -> PreSignGetResp:
    key = extract_gs_key(payload.gs_url)
    if not key:
        raise AppError(ErrorKind.BAD_REQUEST, "gs_urlが不正です")
    url = storage_adapter.gen_pre_signed_get_url(key)

    return PreSignGetResp(url=url)


@final
class _CreateDocumentPayload(BaseModel):
    name: str
    description: str
    gs_key: str


@router.post("/documents")
@inject
async def _create_documents(
        request: Request,
        payload: _CreateDocumentPayload,
        document_repository: DocumentRepository = Depends(
            Provide[AppContainer.document_repository]
        ),
) -> DocumentResp:
    uid: Final[UserId] = request.state.uid
    now: Final[datetime] = datetime.now(timezone.utc)

    gs_file_url = f"gs://{DEFAULT_BUCKET_NAME}/{payload.gs_key}"
    new_document = Document.new(
        uid, payload.name, payload.description, gs_file_url, now
    )
    await document_repository.insert(new_document)

    return DocumentResp.from_model(new_document)


@final
class _UpdateDocumentPayload(BaseModel):
    name: str
    description: str


@router.put("/documents/{document_id}")
@inject
async def _update_documents(
        request: Request,
        document_id: DocumentId,
        payload: _UpdateDocumentPayload,
        document_repository: DocumentRepository = Depends(
            Provide[AppContainer.document_repository]
        ),
) -> DocumentResp:
    uid: Final[UserId] = request.state.uid
    now: Final[datetime] = datetime.now(timezone.utc)

    document = await document_repository.get(document_id)
    if not document:
        raise AppError(
            ErrorKind.NOT_FOUND, f"ドキュメントが見つかりません: {document_id}"
        )
    if document.user_id != uid:
        raise AppError(ErrorKind.FORBIDDEN, f"権限がありません: {uid}")

    document.update(payload.name, payload.description, now)
    await document_repository.update(document)

    return DocumentResp.from_model(document)


@router.delete("/documents/{document_id}")
@inject
async def _delete_documents(
        request: Request,
        document_id: DocumentId,
        storage_adapter: StorageAdapter = Depends(Provide[AppContainer.storage_adapter]),
        openai_adapter: OpenAIAdapter = Depends(Provide[AppContainer.openai_adapter]),
        document_repository: DocumentRepository = Depends(
            Provide[AppContainer.document_repository]
        ),
        assistant_repository: AssistantRepository = Depends(
            Provide[AppContainer.assistant_repository]
        ),
        assistant_fs_repository: AssistantFSRepository = Depends(
            Provide[AppContainer.assistant_fs_repository]
        ),
) -> EmptyResp:
    uid: Final[UserId] = request.state.uid

    document = await document_repository.get(document_id)
    if not document:
        raise AppError(
            ErrorKind.NOT_FOUND, f"ドキュメントが見つかりません: {document_id}"
        )
    if document.user_id != uid:
        raise AppError(ErrorKind.FORBIDDEN, f"権限がありません: {uid}")

    key = extract_gs_key(document.gs_file_url)
    if not key:
        raise AppError(ErrorKind.INTERNAL, "gs_urlが不正です")
    storage_adapter.delete_object(key)

    assistant = await assistant_repository.get(document.id)
    if assistant is not None:
        openai_adapter.delete(assistant.id)
        await document_repository.delete_with_assistant(document.id)
        await assistant_fs_repository.delete(assistant.id)
    else:
        await document_repository.delete(document.id)

    return EmptyResp()


@router.post("/documents/{document_id}/assistants")
@inject
async def _create_assistant(
        request: Request,
        document_id: DocumentId,
        document_repository: DocumentRepository = Depends(
            Provide[AppContainer.document_repository]
        ),
        task_queue_adapter: TaskQueueAdapter = Depends(
            Provide[AppContainer.task_queue_adapter]
        ),
) -> JSONResponse:
    uid: Final[UserId] = request.state.uid

    document = await document_repository.get(document_id)
    if not document:
        raise AppError(
            ErrorKind.NOT_FOUND, f"ドキュメントが見つかりません: {document_id}"
        )
    if document.user_id != uid:
        raise AppError(ErrorKind.FORBIDDEN, f"権限がありません: {uid}")

    task_queue_adapter.send_queue(
        "create-assistant",
        "/subscriber/create_assistant",
        {"document_id": document.id},
    )

    return JSONResponse(content={}, status_code=201)


@router.get("/documents/{document_id}/messages")
@inject
async def _get_messages(
        request: Request,
        document_id: DocumentId,
        document_repository: DocumentRepository = Depends(
            Provide[AppContainer.document_repository]
        ),
        assistant_repository: AssistantRepository = Depends(
            Provide[AppContainer.assistant_repository]
        ),
        message_fs_repository: MessageFSRepository = Depends(
            Provide[AppContainer.message_fs_repository]
        ),
) -> List[MessageResp]:
    uid: Final[UserId] = request.state.uid

    document = await document_repository.get(document_id)
    if not document:
        raise AppError(
            ErrorKind.NOT_FOUND, f"ドキュメントが見つかりません: {document_id}"
        )
    if document.user_id != uid:
        raise AppError(ErrorKind.FORBIDDEN, f"権限がありません: {uid}")
    if document.status != Status.READY_ASSISTANT:
        raise AppError(ErrorKind.BAD_REQUEST, "アシスタントが準備できていません")

    assistant = await assistant_repository.get(document.id)
    if not assistant:
        raise AppError(
            ErrorKind.NOT_FOUND, f"アシスタントが見つかりません: {document.id}"
        )
    messages = await message_fs_repository.find(assistant)

    return [MessageResp.from_model(message) for message in messages]


@final
class _CreateMessagePayload(BaseModel):
    message: str


@router.post("/documents/{document_id}/messages")
@inject
async def _create_message(
        request: Request,
        document_id: DocumentId,
        payload: _CreateMessagePayload,
        document_repository: DocumentRepository = Depends(
            Provide[AppContainer.document_repository]
        ),
        task_queue_adapter: TaskQueueAdapter = Depends(
            Provide[AppContainer.task_queue_adapter]
        ),
) -> JSONResponse:
    uid: Final[UserId] = request.state.uid

    document = await document_repository.get(document_id)
    if not document:
        raise AppError(
            ErrorKind.NOT_FOUND, f"ドキュメントが見つかりません: {document_id}"
        )
    if document.user_id != uid:
        raise AppError(ErrorKind.FORBIDDEN, f"権限がありません: {uid}")
    if document.status != Status.READY_ASSISTANT:
        raise AppError(ErrorKind.BAD_REQUEST, "アシスタントが準備できていません")

    task_queue_adapter.send_queue(
        "create-message",
        "/subscriber/create_message",
        {"document_id": document.id, "message": payload.message},
    )

    return JSONResponse(content={}, status_code=201)
