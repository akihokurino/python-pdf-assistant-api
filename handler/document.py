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
    AssistantRepository,
    OpenAIAdapter,
    AssistantFSRepository,
    MessageFSRepository,
    DocumentSummaryRepository,
)
from config.envs import DEFAULT_BUCKET_NAME
from di.di import AppContainer
from domain.document import Document, DocumentId, Status
from domain.error import AppError, ErrorKind
from domain.user import UserId
from handler.response import (
    DocumentResp,
    EmptyResp,
    DocumentWithUserAndAssistantResp,
    MessageResp,
    TextResp,
)
from handler.util import extract_gs_key

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


@final
class _CreateDocumentPayload(BaseModel):
    name: str
    description: str
    gs_key: str


@router.post("/documents")
@inject
async def _create_document(
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
async def _update_document(
        request: Request,
        document_id: DocumentId,
        payload: _UpdateDocumentPayload,
        document_repository: DocumentRepository = Depends(
            Provide[AppContainer.document_repository]
        ),
) -> DocumentResp:
    uid: Final[UserId] = request.state.uid
    now: Final = datetime.now(timezone.utc)

    document: Final = await document_repository.get(document_id)
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
async def _delete_document(
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

    document: Final = await document_repository.get(document_id)
    if not document:
        raise AppError(
            ErrorKind.NOT_FOUND, f"ドキュメントが見つかりません: {document_id}"
        )
    if document.user_id != uid:
        raise AppError(ErrorKind.FORBIDDEN, f"権限がありません: {uid}")

    key: Final = extract_gs_key(document.gs_file_url)
    if not key:
        raise AppError(ErrorKind.INTERNAL, "gs_urlが不正です")
    storage_adapter.delete_object(key)

    assistant: Final = await assistant_repository.get(document.id)
    if assistant is not None:
        openai_adapter.delete_assistant(assistant.id)
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

    document: Final = await document_repository.get(document_id)
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
) -> list[MessageResp]:
    uid: Final[UserId] = request.state.uid

    document: Final = await document_repository.get(document_id)
    if not document:
        raise AppError(
            ErrorKind.NOT_FOUND, f"ドキュメントが見つかりません: {document_id}"
        )
    if document.user_id != uid:
        raise AppError(ErrorKind.FORBIDDEN, f"権限がありません: {uid}")
    if document.status != Status.READY_ASSISTANT:
        raise AppError(ErrorKind.BAD_REQUEST, "アシスタントが準備できていません")

    assistant: Final = await assistant_repository.get(document.id)
    if not assistant:
        raise AppError(
            ErrorKind.NOT_FOUND, f"アシスタントが見つかりません: {document.id}"
        )
    messages: Final = await message_fs_repository.find(assistant)

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

    document: Final = await document_repository.get(document_id)
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


@router.get("/documents/{document_id}/summaries")
@inject
async def _get_document_summaries(
        request: Request,
        document_id: DocumentId,
        document_repository: DocumentRepository = Depends(
            Provide[AppContainer.document_repository]
        ),
        document_summary_repository: DocumentSummaryRepository = Depends(
            Provide[AppContainer.document_summary_repository]
        ),
) -> list[TextResp]:
    uid: Final[UserId] = request.state.uid

    document: Final = await document_repository.get(document_id)
    if not document:
        raise AppError(
            ErrorKind.NOT_FOUND, f"ドキュメントが見つかりません: {document_id}"
        )
    if document.user_id != uid:
        raise AppError(ErrorKind.FORBIDDEN, f"権限がありません: {uid}")

    summaries: Final = await document_summary_repository.find_by_document(document.id)

    return [TextResp(text=summary.text) for summary in summaries]


@router.post("/documents/{document_id}/summaries")
@inject
async def _summarise_document(
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

    document: Final = await document_repository.get(document_id)
    if not document:
        raise AppError(
            ErrorKind.NOT_FOUND, f"ドキュメントが見つかりません: {document_id}"
        )
    if document.user_id != uid:
        raise AppError(ErrorKind.FORBIDDEN, f"権限がありません: {uid}")

    task_queue_adapter.send_queue(
        "summarise-document",
        "/subscriber/summarise_document",
        {"document_id": document.id},
    )

    return JSONResponse(content={}, status_code=201)
