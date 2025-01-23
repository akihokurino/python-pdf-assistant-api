from datetime import datetime
from typing import Protocol, Any, Tuple, List, Optional

from config.envs import DEFAULT_BUCKET_NAME
from model.document import DocumentId, Document
from model.openai_assistant import OpenaiAssistant, OpenaiAssistantId, OpenaiThreadId
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


class OpenaiAdapter(Protocol):
    def get_answer(self, _assistant: OpenaiAssistant, question: str) -> str: ...

    def create_assistant(
            self, document_id: DocumentId, document_path: str
    ) -> Tuple[OpenaiAssistantId, OpenaiThreadId]: ...

    def delete_assistant(self, assistant_id: OpenaiAssistantId) -> None: ...


class UserRepository(Protocol):
    async def find_users(self) -> List[User]: ...

    async def get_user(self, _id: UserId) -> Optional[User]: ...

    async def get_user_with_documents(
            self, _id: UserId
    ) -> Optional[Tuple[User, List[Document]]]: ...

    async def insert_user(self, item: User) -> None: ...

    async def update_user(self, item: User) -> None: ...

    async def delete_user(self, _id: UserId) -> None: ...


class DocumentRepository(Protocol):
    async def find_documents_by_user(self, user_id: UserId) -> List[Document]: ...

    async def get_document(self, _id: DocumentId) -> Optional[Document]: ...

    async def get_document_with_user(
            self, _id: DocumentId
    ) -> Optional[Tuple[Document, User]]: ...

    async def insert_document(self, item: Document) -> None: ...

    async def update_document(self, item: Document) -> None: ...

    async def delete_document(self, _id: DocumentId) -> None: ...


class OpenaiAssistantRepository(Protocol):
    async def find_past_openai_assistants(
            self, date: datetime
    ) -> List[Tuple[OpenaiAssistant, Document]]: ...

    async def get_assistant(self, _id: DocumentId) -> Optional[OpenaiAssistant]: ...

    async def insert_assistant(self, item: OpenaiAssistant) -> None: ...

    async def insert_assistant_and_update_document(
            self, assistant: OpenaiAssistant, document: Document
    ) -> None: ...

    async def update_assistant(self, item: OpenaiAssistant) -> None: ...

    async def delete_assistant(self, _id: DocumentId) -> None: ...

    async def delete_assistant_and_update_document(
            self, _id: DocumentId, document: Document
    ) -> None: ...
