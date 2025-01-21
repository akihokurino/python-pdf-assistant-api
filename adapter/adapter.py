from typing import Protocol, Any, Tuple

from config.envs import DEFAULT_BUCKET_NAME
from model.document import DocumentId
from model.openai_assistant import OpenaiAssistant, OpenaiAssistantId, OpenaiThreadId


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
    def get_answer(self, _assistant: OpenaiAssistant, question: str) -> str: ...

    def create_assistant(
            self, document_id: DocumentId, document_path: str
    ) -> Tuple[OpenaiAssistantId, OpenaiThreadId]: ...

    def delete_assistant(self, assistant_id: OpenaiAssistantId) -> None: ...
