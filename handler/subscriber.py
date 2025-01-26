import re
from datetime import datetime, timezone
from typing import Final, final, List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from pdfminer.high_level import extract_text
from pydantic import BaseModel

from adapter.adapter import (
    OpenAIAdapter,
    AssistantRepository,
    DocumentRepository,
    StorageAdapter,
    AssistantFSRepository,
    MessageFSRepository, DocumentSummaryRepository, ChatMessage,
)
from di.di import AppContainer
from handler.response import EmptyResp
from handler.util import extract_gs_key
from model.assistant import Assistant, Message
from model.document import DocumentId, Status, DocumentSummary
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

    new_assistant = openai_adapter.create_assistant(
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

    answer = openai_adapter.chat_assistant(assistant, payload.message)

    assistant_message = Message.new(
        assistant.thread_id, "assistant", answer, datetime.now(timezone.utc)
    )
    await message_fs_repository.put(assistant, assistant_message)

    return EmptyResp()


@final
class _SummariseDocumentPayload(BaseModel):
    document_id: DocumentId


@router.post("/subscriber/summarise_document")
@inject
async def _summarise(
        payload: _SummariseDocumentPayload,
        storage_adapter: StorageAdapter = Depends(Provide[AppContainer.storage_adapter]),
        openai_adapter: OpenAIAdapter = Depends(Provide[AppContainer.openai_adapter]),
        document_repository: DocumentRepository = Depends(
            Provide[AppContainer.document_repository]
        ),
        document_summary_repository: DocumentSummaryRepository = Depends(
            Provide[AppContainer.document_summary_repository]
        ),
) -> EmptyResp:
    now: Final[datetime] = datetime.now(timezone.utc)
    document = await document_repository.get(payload.document_id)
    if not document:
        raise AppError(
            ErrorKind.NOT_FOUND, f"ドキュメントが見つかりません: {payload.document_id}"
        )

    key = extract_gs_key(document.gs_file_url)
    if not key:
        raise AppError(ErrorKind.INTERNAL, "ファイルのURLが不正です")
    destination_file_name: Final[str] = f"/tmp/{document.id}_downloaded.pdf"
    storage_adapter.download_object(key, destination_file_name)

    text = extract_text(destination_file_name)
    text = text.replace('-\n', '')
    text = re.sub(r'\s+', ' ', text)

    wc_max: Final = 10000

    def split_text(_text: str) -> List[str]:
        chunks = [_text[i:i + wc_max] for i in range(0, len(_text), wc_max)]
        return chunks

    def create_prompt(_text: str, total: int) -> str:
        return f"""以下は日本語の研究論文の一部です。この論文を簡潔に要約してください。
論文は全部で{total + 1}個に分割されています。

以下のルールに従ってください：
・箇条書き形式で出力する (先頭は「- 」を使う)
・簡潔かつわかりやすく要約する
・不明な専門用語がある場合はそのまま残す

それでは開始します。

日本語の論文の一部:
{_text}

要約:"""

    parted_text = split_text(text)
    summaries: List[DocumentSummary] = []
    for i in range(len(parted_text)):
        messages: List[ChatMessage] = [
            ChatMessage(role="system",
                        content="あなたはPDFを要約する専門家です。あなたは前後に問い合わせした内容を考慮して思慮深い回答をします。"),
            ChatMessage(role="user", content=create_prompt(parted_text[i], len(parted_text)))
        ]
        resp = openai_adapter.chat_completion(messages)
        summaries.append(DocumentSummary.new(document.id, resp, i, now))

    await document_summary_repository.delete_by_document(document.id)
    for summary in summaries:
        await document_summary_repository.insert(summary)

    return EmptyResp()
