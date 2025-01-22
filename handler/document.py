import uuid
from datetime import datetime, timezone
from typing import Final, final

from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from adapter.adapter import (
    StorageAdapter,
    DocumentRepository,
    TaskQueueAdapter,
    OpenaiAssistantRepository,
    OpenaiAdapter,
)
from config.envs import DEFAULT_BUCKET_NAME
from handler.response import DocumentWithUserResp, PreSignUploadResp, PreSignGetResp, DocumentResp, AnswerResp, \
    EmptyResp
from model.document import Document, DocumentId, Status
from model.error import AppError, ErrorKind
from model.user import UserId
from util.gs_url import gs_url_to_key

router: Final[APIRouter] = APIRouter()


@router.get("/documents/{document_id}")
async def _get_document(
        document_id: DocumentId,
        request: Request,
        document_repository: DocumentRepository = Depends(),
) -> DocumentWithUserResp:
    result = document_repository.get_document_with_user(document_id)
    if not result:
        raise AppError(
            ErrorKind.NOT_FOUND, f"ドキュメントが見つかりません: {document_id}"
        )

    return DocumentWithUserResp.from_model(result[1], result[0])


@router.post("/documents/pre_signed_upload_url")
async def _pre_signed_upload_url(
        request: Request,
        storage_adapter: StorageAdapter = Depends(),
) -> PreSignUploadResp:
    uid: Final[UserId] = request.state.uid
    key = f"documents/{uid}/{uuid.uuid4()}.pdf"
    url = storage_adapter.gen_pre_signed_upload_url(key)

    return PreSignUploadResp(url=url, key=key)


@final
class _PreSignedGetUrlPayload(BaseModel):
    gs_url: str


@router.post("/documents/pre_signed_get_url")
async def _pre_signed_get_url(
        request: Request,
        payload: _PreSignedGetUrlPayload,
        storage_adapter: StorageAdapter = Depends(),
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
async def _create_documents(
        request: Request,
        payload: _CreateDocumentPayload,
        document_repository: DocumentRepository = Depends(),
) -> DocumentResp:
    uid: Final[UserId] = request.state.uid
    now: Final[datetime] = datetime.now(timezone.utc)

    gs_file_url = f"gs://{DEFAULT_BUCKET_NAME}/{payload.gs_key}"
    new_document = Document.new(
        uid, payload.name, payload.description, gs_file_url, now
    )
    document_repository.insert_document(new_document)

    return DocumentResp.from_model(new_document)


@router.post("/documents/{document_id}/openai_assistants")
async def _create_openai_assistant(
        document_id: DocumentId,
        request: Request,
        document_repository: DocumentRepository = Depends(),
        task_queue_adapter: TaskQueueAdapter = Depends(),
) -> JSONResponse:
    uid: Final[UserId] = request.state.uid

    document = document_repository.get_document(document_id)
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
    question: str


@router.post("/documents/{document_id}/openai_messages")
async def _create_openai_message(
        document_id: DocumentId,
        request: Request,
        payload: _CreateOpenaiMessagePayload,
        openai_adapter: OpenaiAdapter = Depends(),
        document_repository: DocumentRepository = Depends(),
        openai_assistant_repository: OpenaiAssistantRepository = Depends(),
) -> AnswerResp:
    uid: Final[UserId] = request.state.uid
    now: Final[datetime] = datetime.now(timezone.utc)

    document = document_repository.get_document(document_id)
    if not document:
        raise AppError(
            ErrorKind.NOT_FOUND, f"ドキュメントが見つかりません: {document_id}"
        )
    if document.user_id != uid:
        raise AppError(ErrorKind.FORBIDDEN, f"権限がありません: {uid}")
    if document.status != Status.READY_ASSISTANT:
        raise AppError(ErrorKind.BAD_REQUEST, "アシスタントが準備できていません")

    openai_assistant = openai_assistant_repository.get_assistant(document.id)
    if not openai_assistant:
        raise AppError(
            ErrorKind.NOT_FOUND, f"アシスタントが見つかりません: {document_id}"
        )

    openai_assistant.use(now)
    openai_assistant_repository.update_assistant(openai_assistant)

    answer = openai_adapter.get_answer(openai_assistant, payload.question)

    return AnswerResp(answer=answer)


@final
class _UpdateDocumentPayload(BaseModel):
    name: str
    description: str


@router.put("/documents/{document_id}")
async def _update_documents(
        document_id: DocumentId,
        request: Request,
        payload: _UpdateDocumentPayload,
        document_repository: DocumentRepository = Depends(),
) -> DocumentResp:
    uid: Final[UserId] = request.state.uid
    now: Final[datetime] = datetime.now(timezone.utc)

    document = document_repository.get_document(document_id)
    if not document:
        raise AppError(
            ErrorKind.NOT_FOUND, f"ドキュメントが見つかりません: {document_id}"
        )
    if document.user_id != uid:
        raise AppError(ErrorKind.FORBIDDEN, f"権限がありません: {uid}")

    document.update(payload.name, payload.description, now)
    document_repository.update_document(document)

    return DocumentResp.from_model(document)


@router.delete("/documents/{document_id}")
async def _delete_documents(
        document_id: DocumentId,
        request: Request,
        storage_adapter: StorageAdapter = Depends(),
        document_repository: DocumentRepository = Depends(),
) -> EmptyResp:
    uid: Final[UserId] = request.state.uid

    document = document_repository.get_document(document_id)
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
    document_repository.delete_document(document_id)

    return EmptyResp()
