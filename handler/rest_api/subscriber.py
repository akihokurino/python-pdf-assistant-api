import base64
import re
from datetime import datetime, timezone
from typing import Final, final

import pandas as pd
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
    MessageFSRepository,
    DocumentSummaryRepository,
    ChatMessage,
)
from di.di import AppContainer
from domain.assistant import Assistant, Message
from domain.document import DocumentId, Status, DocumentSummary, Document
from domain.error import AppError, ErrorKind
from domain.user import UserId
from handler.rest_api.response import EmptyResp
from handler.util import extract_gs_key

router: Final = APIRouter()


@final
class PubSubMessage(BaseModel):
    data: str  # base64 encoded


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
    now: Final = datetime.now(timezone.utc)

    already: Final = await assistant_repository.get(payload.document_id)
    if already:
        return EmptyResp()

    document: Final = await document_repository.get(payload.document_id)
    if not document:
        raise AppError(ErrorKind.NOT_FOUND, "ドキュメントが見つかりません")

    document.update_status(Status.READY_ASSISTANT, now)

    key: Final = extract_gs_key(document.gs_file_url)
    if not key:
        raise AppError(ErrorKind.INTERNAL, "ファイルのURLが不正です")
    destination_file_name: Final = f"/tmp/{document.id}_downloaded.pdf"
    await storage_adapter.download_object(key, destination_file_name)

    assistant_id, thread_id = await openai_adapter.create_assistant(
        document.id,
        destination_file_name,
    )
    assistant: Final = Assistant.new(assistant_id, document.id, thread_id, now)
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
    now: Final = datetime.now(timezone.utc)

    document: Final = await document_repository.get(payload.document_id)
    if not document:
        raise AppError(ErrorKind.NOT_FOUND, "ドキュメントが見つかりません")

    assistant: Final = await assistant_repository.get(document.id)
    if not assistant:
        raise AppError(
            ErrorKind.NOT_FOUND, f"アシスタントが見つかりません: {document.id}"
        )

    assistant.use(now)
    await assistant_repository.update(assistant)

    my_message: Final = Message.new(
        assistant.thread_id, "user", payload.message, datetime.now(timezone.utc)
    )
    await message_fs_repository.put(assistant, my_message)

    answer: Final = await openai_adapter.chat_assistant(assistant, payload.message)

    assistant_message: Final = Message.new(
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
    now: Final = datetime.now(timezone.utc)

    document: Final = await document_repository.get(payload.document_id)
    if not document:
        raise AppError(
            ErrorKind.NOT_FOUND, f"ドキュメントが見つかりません: {payload.document_id}"
        )

    key: Final = extract_gs_key(document.gs_file_url)
    if not key:
        raise AppError(ErrorKind.INTERNAL, "ファイルのURLが不正です")
    destination_file_name: Final = f"/tmp/{document.id}_downloaded.pdf"
    await storage_adapter.download_object(key, destination_file_name)

    text = extract_text(destination_file_name)
    text = text.replace("-\n", "")
    text = re.sub(r"\s+", " ", text)

    wc_max: Final = 10000

    def split_text(_text: str) -> list[str]:
        chunks = [_text[_i : _i + wc_max] for _i in range(0, len(_text), wc_max)]
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

    parted_text: Final = split_text(text)
    summaries: Final[list[DocumentSummary]] = []
    for i in range(len(parted_text)):
        messages: list[ChatMessage] = [
            ChatMessage(
                role="system",
                content="あなたはPDFを要約する専門家です。あなたは前後に問い合わせした内容を考慮して思慮深い回答をします。",
            ),
            ChatMessage(
                role="user", content=create_prompt(parted_text[i], len(parted_text))
            ),
        ]
        resp = await openai_adapter.chat_completion(messages)
        summaries.append(DocumentSummary.new(document.id, resp, i, now))

    await document_summary_repository.delete_by_document(document.id)
    for summary in summaries:
        await document_summary_repository.insert(summary)

    return EmptyResp()


@final
class _StorageUploadNotificationPayload(BaseModel):
    message: PubSubMessage


@router.post("/subscriber/storage_upload_notification")
@inject
async def _storage_upload_notification(
    payload: _StorageUploadNotificationPayload,
    storage_adapter: StorageAdapter = Depends(Provide[AppContainer.storage_adapter]),
    document_repository: DocumentRepository = Depends(
        Provide[AppContainer.document_repository]
    ),
) -> EmptyResp:
    now: Final = datetime.now(timezone.utc)

    @final
    class _Params(BaseModel):
        bucket: str
        name: str
        timeCreated: str
        updated: str

    decoded_data: Final = base64.b64decode(payload.message.data).decode("utf-8")
    params: Final = _Params.model_validate_json(decoded_data)

    match: Final = re.search(r"csv/([^/]+)/[\w-]+\.csv", params.name)
    if match:
        uid = UserId(match.group(1))
    else:
        raise AppError(ErrorKind.INTERNAL, "ファイルのURLが不正です")

    destination_file_name: Final = f"/tmp/{uid}_downloaded.csv"
    await storage_adapter.download_object(params.name, destination_file_name)

    df: Final = pd.read_csv(
        destination_file_name, header=None, names=["name", "description", "gs_path"]
    )
    documents: list[Document] = [
        Document.new(
            uid, str(row["name"]), str(row["description"]), str(row["gs_path"]), now
        )
        for _, row in df.iterrows()
    ]

    for document in documents:
        await document_repository.insert(document)

    return EmptyResp()
