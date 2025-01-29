import uuid
from typing import Final, final

from dependency_injector.wiring import Provide, inject
from fastapi import Request, Depends, APIRouter
from pydantic import BaseModel

from adapter.adapter import StorageAdapter
from di.di import AppContainer
from domain.error import AppError, ErrorKind
from domain.user import UserId
from handler.rest_api.response import PreSignUploadResp, PreSignGetResp
from handler.util import extract_gs_key

router: Final = APIRouter()


@final
class _PreSignedUploadUrlPayload(BaseModel):
    path: str


@router.post("/pre_signed_upload_url")
@inject
async def _pre_signed_upload_url(
    request: Request,
    payload: _PreSignedUploadUrlPayload,
    storage_adapter: StorageAdapter = Depends(Provide[AppContainer.storage_adapter]),
) -> PreSignUploadResp:
    uid: Final[UserId] = request.state.uid

    if payload.path != "documents" and payload.path != "csv":
        raise AppError(ErrorKind.BAD_REQUEST, "pathが不正です")

    ext = "pdf"
    content_type = "application/pdf"
    if payload.path == "csv":
        ext = "csv"
        content_type = "text/csv"

    key: Final = f"{payload.path}/{uid}/{uuid.uuid4()}.{ext}"
    url: Final = await storage_adapter.gen_pre_signed_upload_url(key, content_type)

    return PreSignUploadResp(url=url, key=key)


@final
class _PreSignedGetUrlPayload(BaseModel):
    gs_url: str


@router.post("/pre_signed_get_url")
@inject
async def _pre_signed_get_url(
    payload: _PreSignedGetUrlPayload,
    storage_adapter: StorageAdapter = Depends(Provide[AppContainer.storage_adapter]),
) -> PreSignGetResp:
    key: Final = extract_gs_key(payload.gs_url)
    if not key:
        raise AppError(ErrorKind.BAD_REQUEST, "gs_urlが不正です")
    url: Final = await storage_adapter.gen_pre_signed_get_url(key)

    return PreSignGetResp(url=url)
