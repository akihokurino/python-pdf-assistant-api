import dataclasses
from datetime import datetime
from typing import Protocol, Any, Tuple, List, Optional, Literal, final

from config.envs import DEFAULT_BUCKET_NAME
from domain.assistant import (
    Assistant,
    AssistantId,
    ThreadId,
    Message,
)
from domain.document import DocumentId, Document, DocumentSummary
from domain.user import User, UserId


class StorageAdapter(Protocol):
    async def download_object(
        self,
        key: str,
        destination_file_name: str,
        bucket_name: str = DEFAULT_BUCKET_NAME,
    ) -> None: ...

    async def gen_pre_signed_upload_url(
        self,
        key: str,
        content_type: str,
        bucket_name: str = DEFAULT_BUCKET_NAME,
        expiration_minutes: int = 15,
    ) -> str: ...

    async def gen_pre_signed_get_url(
        self,
        key: str,
        bucket_name: str = DEFAULT_BUCKET_NAME,
        expiration_minutes: int = 15,
    ) -> str: ...

    async def delete_object(
        self, key: str, bucket_name: str = DEFAULT_BUCKET_NAME
    ) -> None: ...


class TaskQueueAdapter(Protocol):
    def send_queue(self, name: str, path: str, payload: dict[str, Any]) -> None: ...


class LogAdapter(Protocol):
    def log_info(self, message: str) -> None: ...

    def log_error(self, e: Exception) -> None: ...


@final
@dataclasses.dataclass(frozen=True)
class ChatMessage:
    role: Literal["user", "system"]
    content: str


class OpenAIAdapter(Protocol):
    def chat_assistant(self, _assistant: Assistant, message: str) -> str: ...

    def create_assistant(
        self, document_id: DocumentId, document_path: str
    ) -> Tuple[AssistantId, ThreadId]: ...

    def delete_assistant(self, assistant_id: AssistantId) -> None: ...

    def chat_completion(self, messages: List[ChatMessage]) -> str: ...


@final
@dataclasses.dataclass(frozen=True)
class Pager:
    cursor: Optional[str]
    limit: int

    def limit_with_next_one(self) -> int:
        return self.limit + 1


class UserRepository(Protocol):
    async def find(self) -> List[User]: ...

    async def get(self, _id: UserId) -> Optional[User]: ...

    async def get_with_documents(
        self, _id: UserId
    ) -> Optional[Tuple[User, List[Document]]]: ...

    async def insert(self, user: User) -> None: ...

    async def update(self, user: User) -> None: ...

    async def delete(self, _id: UserId) -> None: ...


class DocumentRepository(Protocol):
    async def find_by_user(
        self, user_id: UserId, limit: Optional[int] = None
    ) -> List[Document]: ...

    async def find_by_user_with_pager(
        self, user_id: UserId, pager: Pager
    ) -> tuple[list[Document], str]: ...

    async def get(self, _id: DocumentId) -> Optional[Document]: ...

    async def get_with_user_and_assistant(
        self, _id: DocumentId
    ) -> Optional[Tuple[Document, User, Optional[Assistant]]]: ...

    async def insert(self, document: Document) -> None: ...

    async def update(self, document: Document) -> None: ...

    async def delete(self, _id: DocumentId) -> None: ...

    async def delete_with_assistant(self, _id: DocumentId) -> None: ...


class DocumentSummaryRepository(Protocol):
    async def find_by_document(
        self, document_id: DocumentId
    ) -> List[DocumentSummary]: ...

    async def insert(self, summary: DocumentSummary) -> None: ...

    async def delete_by_document(self, document_id: DocumentId) -> None: ...


class AssistantRepository(Protocol):
    async def find_past(self, date: datetime) -> List[Tuple[Assistant, Document]]: ...

    async def get(self, _id: DocumentId) -> Optional[Assistant]: ...

    async def insert(self, assistant: Assistant) -> None: ...

    async def insert_with_update_document(
        self, assistant: Assistant, document: Document
    ) -> None: ...

    async def update(self, assistant: Assistant) -> None: ...

    async def delete(self, _id: DocumentId) -> None: ...

    async def delete_with_update_document(
        self, _id: DocumentId, document: Document
    ) -> None: ...


class AssistantFSRepository(Protocol):
    async def put(self, assistant: Assistant) -> None: ...

    async def delete(self, _id: AssistantId) -> None: ...


class MessageFSRepository(Protocol):
    async def find(self, assistant: Assistant) -> List[Message]: ...

    async def put(self, assistant: Assistant, message: Message) -> None: ...
