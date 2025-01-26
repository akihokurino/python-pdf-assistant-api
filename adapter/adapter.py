from datetime import datetime
from typing import Protocol, Any, Tuple, List, Optional

from config.envs import DEFAULT_BUCKET_NAME
from model.assistant import (
    Assistant,
    AssistantId,
    ThreadId,
    Message,
)
from model.document import DocumentId, Document
from model.user import User, UserId


class StorageAdapter(Protocol):
    def download_object(
            self,
            key: str,
            destination_file_name: str,
            bucket_name: str = DEFAULT_BUCKET_NAME,
    ) -> None: ...

    def gen_pre_signed_upload_url(
            self,
            key: str,
            bucket_name: str = DEFAULT_BUCKET_NAME,
            expiration_minutes: int = 15,
    ) -> str: ...

    def gen_pre_signed_get_url(
            self,
            key: str,
            bucket_name: str = DEFAULT_BUCKET_NAME,
            expiration_minutes: int = 15,
    ) -> str: ...

    def delete_object(
            self, key: str, bucket_name: str = DEFAULT_BUCKET_NAME
    ) -> None: ...


class TaskQueueAdapter(Protocol):
    def send_queue(self, name: str, path: str, payload: dict[str, Any]) -> None: ...


class LogAdapter(Protocol):
    def log_info(self, message: str) -> None: ...

    def log_error(self, e: Exception) -> None: ...


class OpenAIAdapter(Protocol):
    def get_answer(self, _assistant: Assistant, message: str) -> str: ...

    def create(
            self, document_id: DocumentId, document_path: str
    ) -> Tuple[AssistantId, ThreadId]: ...

    def delete(self, assistant_id: AssistantId) -> None: ...


class UserRepository(Protocol):
    async def find(self) -> List[User]: ...

    async def get(self, _id: UserId) -> Optional[User]: ...

    async def get_with_documents(
            self, _id: UserId
    ) -> Optional[Tuple[User, List[Document]]]: ...

    async def insert(self, item: User) -> None: ...

    async def update(self, item: User) -> None: ...

    async def delete(self, _id: UserId) -> None: ...


class DocumentRepository(Protocol):
    async def find_by_user(self, user_id: UserId) -> List[Document]: ...

    async def get(self, _id: DocumentId) -> Optional[Document]: ...

    async def get_with_user_and_assistant(
            self, _id: DocumentId
    ) -> Optional[Tuple[Document, User, Optional[Assistant]]]: ...

    async def insert(self, item: Document) -> None: ...

    async def update(self, item: Document) -> None: ...

    async def delete(self, _id: DocumentId) -> None: ...

    async def delete_with_assistant(self, _id: DocumentId) -> None: ...


class AssistantRepository(Protocol):
    async def find_past(self, date: datetime) -> List[Tuple[Assistant, Document]]: ...

    async def get(self, _id: DocumentId) -> Optional[Assistant]: ...

    async def insert(self, item: Assistant) -> None: ...

    async def insert_with_update_document(
            self, assistant: Assistant, document: Document
    ) -> None: ...

    async def update(self, item: Assistant) -> None: ...

    async def delete(self, _id: DocumentId) -> None: ...

    async def delete_with_update_document(
            self, _id: DocumentId, document: Document
    ) -> None: ...


class AssistantFSRepository(Protocol):
    async def put(self, item: Assistant) -> None: ...

    async def delete(self, _id: AssistantId) -> None: ...


class MessageFSRepository(Protocol):
    async def find(self, assistant: Assistant) -> List[Message]: ...

    async def put(self, assistant: Assistant, message: Message) -> None: ...
