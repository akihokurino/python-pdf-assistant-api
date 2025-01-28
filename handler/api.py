import pkgutil
import uuid
from contextlib import asynccontextmanager
from typing import Final, Any, AsyncGenerator, final

import uvicorn
from dependency_injector.wiring import Provide, inject
from fastapi import FastAPI
from fastapi import Request, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import handler
from adapter.adapter import StorageAdapter
from di.di import container, AppContainer
from domain.error import AppError, ErrorKind
from domain.user import UserId
from handler.document import router as document_router
from handler.me import router as me_router
from handler.middleware.auth import AuthMiddleware
from handler.middleware.error import ErrorMiddleware
from handler.middleware.log import LogMiddleware
from handler.response import EmptyResp, PreSignUploadResp, PreSignGetResp
from handler.subscriber import router as subscriber_router
from handler.user import router as user_router
from handler.util import extract_gs_key


@asynccontextmanager
async def _lifespan(_app: FastAPI) -> AsyncGenerator[None, Any]:
    modules = [
        f"handler.{name}" for _, name, _ in pkgutil.iter_modules(handler.__path__)
    ]
    container.wire(modules=modules)
    _app.container = container  # type: ignore
    yield


app: Final[FastAPI] = FastAPI(lifespan=_lifespan)
app.add_middleware(AuthMiddleware)
app.add_middleware(LogMiddleware)
app.add_middleware(ErrorMiddleware)
app.include_router(me_router)
app.include_router(user_router)
app.include_router(document_router)
app.include_router(subscriber_router)


@app.exception_handler(RequestValidationError)
async def _validation_exception_handler(exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "message": "不正なリクエストです",
            "detail": exc.errors(),
        },
    )


@app.get("/debug")
@inject
async def _debug() -> EmptyResp:
    return EmptyResp()


@final
class _PreSignedUploadUrlPayload(BaseModel):
    path: str


@app.post("/pre_signed_upload_url")
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


@app.post("/pre_signed_get_url")
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


def start() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="debug")
