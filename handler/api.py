import pkgutil
from contextlib import asynccontextmanager
from typing import Final, Any, AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from di.di import container
from handler import api_handler
from handler.api_handler.document import router as document_router
from handler.api_handler.me import router as me_router
from handler.api_handler.middleware.auth import AuthMiddleware
from handler.api_handler.middleware.error import ErrorMiddleware
from handler.api_handler.middleware.log import LogMiddleware
from handler.api_handler.pre_sign_url import router as pre_sign_url_router
from handler.api_handler.subscriber import router as subscriber_router
from handler.api_handler.user import router as user_router


@asynccontextmanager
async def _lifespan(_app: FastAPI) -> AsyncGenerator[None, Any]:
    modules = [
        f"handler.api_handler.{name}"
        for _, name, _ in pkgutil.iter_modules(api_handler.__path__)
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
app.include_router(pre_sign_url_router)


@app.exception_handler(RequestValidationError)
async def _validation_exception_handler(exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "message": "不正なリクエストです",
            "detail": exc.errors(),
        },
    )


def start() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="debug")
