import pkgutil
from contextlib import asynccontextmanager
from typing import Final, Any, AsyncGenerator

import uvicorn
from dependency_injector.wiring import Provide, inject
from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

import handler
from adapter.adapter import AssistantFSRepository
from di.di import container, AppContainer
from handler.document import router as document_router
from handler.me import router as me_router
from handler.middleware.auth import AuthMiddleware
from handler.middleware.error import ErrorMiddleware
from handler.middleware.log import LogMiddleware
from handler.response import EmptyResp
from handler.subscriber import router as subscriber_router
from handler.user import router as user_router
from model.assistant import AssistantId


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
async def _debug(
    assistant_fs_repository: AssistantFSRepository = Depends(
        Provide[AppContainer.assistant_fs_repository]
    ),
) -> EmptyResp:
    await assistant_fs_repository.delete(AssistantId("asst_GjNy30WZSKq52kPp70dXWfyC"))
    return EmptyResp()


def start() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="debug")
