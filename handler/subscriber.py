from datetime import datetime, timezone
from typing import Final, final

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from adapter.adapter import (
    OpenaiAdapter,
    OpenaiAssistantRepository,
    DocumentRepository,
    StorageAdapter,
    OpenaiAssistantFSRepository, OpenaiMessageFSRepository,
)
from di.di import AppContainer
from handler.response import EmptyResp
from model.document import DocumentId, Status
from model.error import AppError, ErrorKind
from model.openai_assistant import OpenaiAssistant, OpenaiMessage
from util.gs_url import gs_url_to_key

router: Final[APIRouter] = APIRouter()


@final
class _CreateOpenaiAssistantPayload(BaseModel):
    document_id: DocumentId


@router.post("/subscriber/create_openai_assistant")
@inject
async def _create_openai_assistant(
        payload: _CreateOpenaiAssistantPayload,
        openai_adapter: OpenaiAdapter = Depends(Provide[AppContainer.openai_adapter]),
        storage_adapter: StorageAdapter = Depends(Provide[AppContainer.storage_adapter]),
        openai_assistant_repository: OpenaiAssistantRepository = Depends(
            Provide[AppContainer.openai_assistant_repository]),
        document_repository: DocumentRepository = Depends(Provide[AppContainer.document_repository]),
        openai_assistant_fs_repository: OpenaiAssistantFSRepository = Depends(
            Provide[AppContainer.openai_assistant_fs_repository]),
) -> EmptyResp:
    now: Final[datetime] = datetime.now(timezone.utc)
    assistant = await openai_assistant_repository.get(payload.document_id)
    if assistant:
        return EmptyResp()

    document = await document_repository.get(payload.document_id)
    if not document:
        raise AppError(ErrorKind.NOT_FOUND, "ドキュメントが見つかりません")

    document.update_status(Status.READY_ASSISTANT, now)

    key = gs_url_to_key(document.gs_file_url)
    if not key:
        raise AppError(ErrorKind.INTERNAL, "ファイルのURLが不正です")
    destination_file_name: Final[str] = f"/tmp/{document.id}_downloaded.pdf"
    storage_adapter.download_object(key, destination_file_name)

    new_assistant = openai_adapter.create(
        document.id,
        destination_file_name,
    )
    openai_assistant = OpenaiAssistant.new(
        new_assistant[0], document.id, new_assistant[1], now
    )
    await openai_assistant_repository.insert_with_update_document(
        openai_assistant, document
    )
    await openai_assistant_fs_repository.put(openai_assistant)

    return EmptyResp()


@final
class _CreateOpenaiMessagePayload(BaseModel):
    document_id: DocumentId
    message: str


@router.post("/subscriber/create_openai_message")
@inject
async def _create_openai_message(
        payload: _CreateOpenaiMessagePayload,
        openai_adapter: OpenaiAdapter = Depends(Provide[AppContainer.openai_adapter]),
        openai_assistant_repository: OpenaiAssistantRepository = Depends(
            Provide[AppContainer.openai_assistant_repository]),
        document_repository: DocumentRepository = Depends(Provide[AppContainer.document_repository]),
        openai_message_fs_repository: OpenaiMessageFSRepository = Depends(
            Provide[AppContainer.openai_message_fs_repository]),
) -> EmptyResp:
    now: Final[datetime] = datetime.now(timezone.utc)

    document = await document_repository.get(payload.document_id)
    if not document:
        raise AppError(ErrorKind.NOT_FOUND, "ドキュメントが見つかりません")

    openai_assistant = await openai_assistant_repository.get(document.id)
    if not openai_assistant:
        raise AppError(
            ErrorKind.NOT_FOUND, f"アシスタントが見つかりません: {document.id}"
        )

    openai_assistant.use(now)
    await openai_assistant_repository.update(openai_assistant)

    my_message = OpenaiMessage.new(openai_assistant.thread_id, "user", payload.message, now)
    await openai_message_fs_repository.put(openai_assistant, my_message)
    answer = openai_adapter.get_answer(openai_assistant, payload.message)
    assistant_message = OpenaiMessage.new(
        openai_assistant.thread_id, "assistant", answer, now
    )
    await openai_message_fs_repository.put(openai_assistant, assistant_message)

    return EmptyResp()
