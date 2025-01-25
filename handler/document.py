import uuid
from datetime import datetime, timezone
from typing import Final, final

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from adapter.adapter import (
    StorageAdapter,
    DocumentRepository,
    TaskQueueAdapter,
    OpenaiAssistantRepository,
    OpenaiAdapter,
    OpenaiAssistantFSRepository,
)
from config.envs import DEFAULT_BUCKET_NAME
from di.di import AppContainer
from handler.response import (
    DocumentWithUserResp,
    PreSignUploadResp,
    PreSignGetResp,
    DocumentResp,
    EmptyResp,
)
from model.document import Document, DocumentId, Status
from model.error import AppError, ErrorKind
from model.user import UserId
from util.gs_url import gs_url_to_key

router: Final[APIRouter] = APIRouter()


@router.get("/documents/{document_id}")
@inject
async def _get_document(
        document_id: DocumentId,
        document_repository: DocumentRepository = Depends(Provide[AppContainer.document_repository]),
) -> DocumentWithUserResp:
    result = await document_repository.get_with_user(document_id)
    if not result:
        raise AppError(
            ErrorKind.NOT_FOUND, f"ドキュメントが見つかりません: {document_id}"
        )

    return DocumentWithUserResp.from_model(result[1], result[0])


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
    key = gs_url_to_key(payload.gs_url)
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
        document_repository: DocumentRepository = Depends(Provide[AppContainer.document_repository]),
) -> DocumentResp:
    uid: Final[UserId] = request.state.uid
    now: Final[datetime] = datetime.now(timezone.utc)

    gs_file_url = f"gs://{DEFAULT_BUCKET_NAME}/{payload.gs_key}"
    new_document = Document.new(
        uid, payload.name, payload.description, gs_file_url, now
    )
    await document_repository.insert(new_document)

    return DocumentResp.from_model(new_document)


@router.post("/documents/{document_id}/openai_assistants")
@inject
async def _create_openai_assistant(
        document_id: DocumentId,
        request: Request,
        document_repository: DocumentRepository = Depends(Provide[AppContainer.document_repository]),
        task_queue_adapter: TaskQueueAdapter = Depends(Provide[AppContainer.task_queue_adapter]),
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
        "create-openai-assistant",
        "/subscriber/create_openai_assistant",
        {"document_id": document.id},
    )

    return JSONResponse(content={}, status_code=201)


@final
class _CreateOpenaiMessagePayload(BaseModel):
    message: str


@router.post("/documents/{document_id}/openai_messages")
@inject
async def _create_openai_message(
        document_id: DocumentId,
        request: Request,
        payload: _CreateOpenaiMessagePayload,
        document_repository: DocumentRepository = Depends(Provide[AppContainer.document_repository]),
        task_queue_adapter: TaskQueueAdapter = Depends(Provide[AppContainer.task_queue_adapter]),
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
        "create-openai-message",
        "/subscriber/create_openai_message",
        {"document_id": document.id, "message": payload.message},
    )

    return JSONResponse(content={}, status_code=201)


@final
class _UpdateDocumentPayload(BaseModel):
    name: str
    description: str


@router.put("/documents/{document_id}")
@inject
async def _update_documents(
        document_id: DocumentId,
        request: Request,
        payload: _UpdateDocumentPayload,
        document_repository: DocumentRepository = Depends(Provide[AppContainer.document_repository]),
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
        document_id: DocumentId,
        request: Request,
        storage_adapter: StorageAdapter = Depends(Provide[AppContainer.storage_adapter]),
        openai_adapter: OpenaiAdapter = Depends(Provide[AppContainer.openai_adapter]),
        document_repository: DocumentRepository = Depends(Provide[AppContainer.document_repository]),
        openai_assistant_repository: OpenaiAssistantRepository = Depends(
            Provide[AppContainer.openai_assistant_repository]),
        openai_assistant_fs_repository: OpenaiAssistantFSRepository = Depends(
            Provide[AppContainer.openai_assistant_fs_repository]),
) -> EmptyResp:
    uid: Final[UserId] = request.state.uid

    document = await document_repository.get(document_id)
    if not document:
        raise AppError(
            ErrorKind.NOT_FOUND, f"ドキュメントが見つかりません: {document_id}"
        )
    if document.user_id != uid:
        raise AppError(ErrorKind.FORBIDDEN, f"権限がありません: {uid}")

    key = gs_url_to_key(document.gs_file_url)
    if not key:
        raise AppError(ErrorKind.INTERNAL, "gs_urlが不正です")
    storage_adapter.delete_object(key)

    assistant = await openai_assistant_repository.get(document.id)
    if assistant is not None:
        openai_adapter.delete(assistant.id)
        await openai_assistant_fs_repository.delete(assistant.id)
    await document_repository.delete_with_assistant(document_id)

    return EmptyResp()
