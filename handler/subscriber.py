from datetime import datetime, timezone
from typing import Final, final

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from adapter.adapter import (
    OpenAIAdapter,
    AssistantRepository,
    DocumentRepository,
    StorageAdapter,
    AssistantFSRepository,
    MessageFSRepository,
)
from di.di import AppContainer
from handler.response import EmptyResp
from handler.util import extract_gs_key
from model.assistant import Assistant, Message
from model.document import DocumentId, Status
from model.error import AppError, ErrorKind

router: Final[APIRouter] = APIRouter()


@final
class _CreateAssistantPayload(BaseModel):
    document_id: DocumentId


@router.post("/subscriber/create_assistant")
@inject
async def _create_assistant(
        payload: _CreateAssistantPayload,
        openai_adapter: OpenAIAdapter = Depends(Provide[AppContainer.openai_adapter]),
        storage_adapter: StorageAdapter = Depends(Provide[AppContainer.storage_adapter]),
        assistant_repository: AssistantRepository = Depends(
            Provide[AppContainer.assistant_repository]
        ),
        document_repository: DocumentRepository = Depends(
            Provide[AppContainer.document_repository]
        ),
        assistant_fs_repository: AssistantFSRepository = Depends(
            Provide[AppContainer.assistant_fs_repository]
        ),
) -> EmptyResp:
    now: Final[datetime] = datetime.now(timezone.utc)
    assistant = await assistant_repository.get(payload.document_id)
    if assistant:
        return EmptyResp()

    document = await document_repository.get(payload.document_id)
    if not document:
        raise AppError(ErrorKind.NOT_FOUND, "ドキュメントが見つかりません")

    document.update_status(Status.READY_ASSISTANT, now)

    key = extract_gs_key(document.gs_file_url)
    if not key:
        raise AppError(ErrorKind.INTERNAL, "ファイルのURLが不正です")
    destination_file_name: Final[str] = f"/tmp/{document.id}_downloaded.pdf"
    storage_adapter.download_object(key, destination_file_name)

    new_assistant = openai_adapter.create(
        document.id,
        destination_file_name,
    )
    assistant = Assistant.new(new_assistant[0], document.id, new_assistant[1], now)
    await assistant_repository.insert_with_update_document(assistant, document)
    await assistant_fs_repository.put(assistant)

    return EmptyResp()


@final
class _CreateMessagePayload(BaseModel):
    document_id: DocumentId
    message: str


@router.post("/subscriber/create_message")
@inject
async def _create_message(
        payload: _CreateMessagePayload,
        openai_adapter: OpenAIAdapter = Depends(Provide[AppContainer.openai_adapter]),
        assistant_repository: AssistantRepository = Depends(
            Provide[AppContainer.assistant_repository]
        ),
        document_repository: DocumentRepository = Depends(
            Provide[AppContainer.document_repository]
        ),
        message_fs_repository: MessageFSRepository = Depends(
            Provide[AppContainer.message_fs_repository]
        ),
) -> EmptyResp:
    now: Final[datetime] = datetime.now(timezone.utc)

    document = await document_repository.get(payload.document_id)
    if not document:
        raise AppError(ErrorKind.NOT_FOUND, "ドキュメントが見つかりません")

    assistant = await assistant_repository.get(document.id)
    if not assistant:
        raise AppError(
            ErrorKind.NOT_FOUND, f"アシスタントが見つかりません: {document.id}"
        )

    assistant.use(now)
    await assistant_repository.update(assistant)

    my_message = Message.new(
        assistant.thread_id, "user", payload.message, datetime.now(timezone.utc)
    )
    await message_fs_repository.put(assistant, my_message)

    answer = openai_adapter.get_answer(assistant, payload.message)

    assistant_message = Message.new(
        assistant.thread_id, "assistant", answer, datetime.now(timezone.utc)
    )
    await message_fs_repository.put(assistant, assistant_message)

    return EmptyResp()
