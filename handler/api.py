from typing import Final

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from adapter.adapter import UserRepository, DocumentRepository, OpenaiAssistantRepository, StorageAdapter, \
    TaskQueueAdapter, LogAdapter, OpenaiAdapter
from di.di import use_user_repo, use_document_repo, use_openai_assistant_repo, use_storage, use_task_queue, use_log, \
    use_openai
from handler.document import router as document_router
from handler.me import router as me_router
from handler.subscriber import router as subscriber_router
from handler.user import router as user_router
from middleware.auth import AuthMiddleware
from middleware.error import ErrorMiddleware
from middleware.log import LogMiddleware

app: Final[FastAPI] = FastAPI()
app.add_middleware(AuthMiddleware)
app.add_middleware(LogMiddleware)
app.add_middleware(ErrorMiddleware)
app.include_router(me_router)
app.include_router(user_router)
app.include_router(document_router)
app.include_router(subscriber_router)

app.dependency_overrides[StorageAdapter] = use_storage
app.dependency_overrides[TaskQueueAdapter] = use_task_queue
app.dependency_overrides[LogAdapter] = use_log
app.dependency_overrides[OpenaiAdapter] = use_openai
app.dependency_overrides[UserRepository] = use_user_repo
app.dependency_overrides[DocumentRepository] = use_document_repo
app.dependency_overrides[OpenaiAssistantRepository] = use_openai_assistant_repo


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
