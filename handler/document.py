import os
import re
import uuid
from datetime import datetime, timezone
from typing import Final, final, Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from handler.response import document_resp
from infra.cloud_sql.document import (
    insert_document,
    get_document,
    update_document,
    delete_document,
)
from infra.cloud_storage import (
    gen_pre_signed_upload_url,
    bucket_name,
    gen_pre_signed_get_url,
    delete_object,
)
from model.document import Document, DocumentId
from model.error import AppError, ErrorKind
from model.user import UserId

router: Final[APIRouter] = APIRouter()
_project_id: Final[str] = os.getenv("PROJECT_ID", "")


@router.get("/documents/{document_id}")
def _get_document(document_id: DocumentId, request: Request) -> JSONResponse:
    document = get_document(document_id)
    if not document:
        raise AppError(
            ErrorKind.NOT_FOUND, f"ドキュメントが見つかりません: {document_id}"
        )

    return JSONResponse(content=document_resp(document), status_code=200)


@router.post("/documents/pre_signed_upload_url")
def _pre_signed_upload_url(
    request: Request,
) -> JSONResponse:
    uid: Final[UserId] = request.state.uid
    key = f"documents/{uid}/{uuid.uuid4()}.pdf"
    url = gen_pre_signed_upload_url(key)

    return JSONResponse(
        content={
            "url": url,
            "key": key,
        },
        status_code=200,
    )


@final
class _PreSignedGetUrlPayload(BaseModel):
    gs_url: str


def _gs_url_to_key(gs_url: str) -> Optional[str]:
    match = re.match(r"gs://[^/]+/(.+)", gs_url)
    if match:
        return match.group(1)
    return None


@router.post("/documents/pre_signed_get_url")
def _pre_signed_get_url(
    request: Request,
    payload: _PreSignedGetUrlPayload,
) -> JSONResponse:
    key = _gs_url_to_key(payload.gs_url)
    if not key:
        raise AppError(ErrorKind.BAD_REQUEST, "gs_urlが不正です")
    print(key)
    url = gen_pre_signed_get_url(key)

    return JSONResponse(
        content={
            "url": url,
        },
        status_code=200,
    )


@final
class _CreateDocumentPayload(BaseModel):
    name: str
    description: str
    gs_key: str


@router.post("/documents")
def _create_documents(
    request: Request,
    payload: _CreateDocumentPayload,
) -> JSONResponse:
    uid: Final[UserId] = request.state.uid
    now: Final[datetime] = datetime.now(timezone.utc)

    gs_file_url = f"gs://{bucket_name}/{payload.gs_key}"
    new_document = Document.new(
        uid, payload.name, payload.description, gs_file_url, now
    )
    insert_document(new_document)

    return JSONResponse(content=document_resp(new_document), status_code=200)


@final
class _UpdateDocumentPayload(BaseModel):
    name: str
    description: str


@router.put("/documents/{document_id}")
def _update_documents(
    document_id: DocumentId,
    request: Request,
    payload: _UpdateDocumentPayload,
) -> JSONResponse:
    uid: Final[UserId] = request.state.uid
    now: Final[datetime] = datetime.now(timezone.utc)

    document = get_document(document_id)
    if not document:
        raise AppError(
            ErrorKind.NOT_FOUND, f"ドキュメントが見つかりません: {document_id}"
        )

    if document.user_id != uid:
        raise AppError(ErrorKind.FORBIDDEN, f"権限がありません: {uid}")

    document.update(payload.name, payload.description, now)
    update_document(document)

    return JSONResponse(content=document_resp(document), status_code=200)


@router.delete("/documents/{document_id}")
def _delete_documents(
    document_id: DocumentId,
    request: Request,
) -> JSONResponse:
    uid: Final[UserId] = request.state.uid

    document = get_document(document_id)
    if not document:
        raise AppError(
            ErrorKind.NOT_FOUND, f"ドキュメントが見つかりません: {document_id}"
        )

    if document.user_id != uid:
        raise AppError(ErrorKind.FORBIDDEN, f"権限がありません: {uid}")

    key = _gs_url_to_key(document.gs_file_url)
    if not key:
        raise AppError(ErrorKind.INTERNAL, "gs_urlが不正です")

    delete_object(key)
    delete_document(document_id)

    return JSONResponse(content={}, status_code=200)
