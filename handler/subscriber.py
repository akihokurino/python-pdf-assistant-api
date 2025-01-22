from datetime import datetime, timezone
from typing import Final, final

from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel

from adapter.adapter import (
    OpenaiAdapter,
    OpenaiAssistantRepository,
    DocumentRepository,
    StorageAdapter,
)
from handler.response import EmptyResp
from model.document import DocumentId, Status
from model.error import AppError, ErrorKind
from model.openai_assistant import OpenaiAssistant
from util.gs_url import gs_url_to_key

router: Final[APIRouter] = APIRouter()


@final
class _CreateOpenaiAssistantPayload(BaseModel):
    document_id: DocumentId


@router.post("/subscriber/create_openai_assistant")
def _create_openai_assistant(
        request: Request,
        payload: _CreateOpenaiAssistantPayload,
        openai_adapter: OpenaiAdapter = Depends(),
        storage_adapter: StorageAdapter = Depends(),
        openai_assistant_repository: OpenaiAssistantRepository = Depends(),
        document_repository: DocumentRepository = Depends(),
) -> EmptyResp:
    now: Final[datetime] = datetime.now(timezone.utc)
    assistant = openai_assistant_repository.get_assistant(payload.document_id)
    if assistant:
        return EmptyResp()

    document = document_repository.get_document(payload.document_id)
    if not document:
        raise AppError(ErrorKind.NOT_FOUND, "ドキュメントが見つかりません")

    document.update_status(Status.READY_ASSISTANT, now)

    key = gs_url_to_key(document.gs_file_url)
    if not key:
        raise AppError(ErrorKind.INTERNAL, "ファイルのURLが不正です")
    destination_file_name: Final[str] = f"/tmp/{document.id}_downloaded.pdf"
    storage_adapter.download_object(key, destination_file_name)

    new_assistant = openai_adapter.create_assistant(
        document.id,
        destination_file_name,
    )
    openai_assistant = OpenaiAssistant.new(
        new_assistant[0], document.id, new_assistant[1], now
    )
    openai_assistant_repository.insert_assistant_and_update_document(
        openai_assistant, document
    )

    return EmptyResp()
