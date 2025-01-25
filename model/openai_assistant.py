from __future__ import annotations

import uuid
from datetime import datetime
from typing import final, NewType, Final, Literal

from model.document import DocumentId

OpenaiAssistantId = NewType("OpenaiAssistantId", str)
OpenaiThreadId = NewType("OpenaiThreadId", str)
OpenaiMessageId = NewType("OpenaiMessageId", str)


@final
class OpenaiAssistant:
    def __init__(
            self,
            _id: OpenaiAssistantId,
            document_id: DocumentId,
            thread_id: OpenaiThreadId,
            used_at: datetime,
            created_at: datetime,
            updated_at: datetime,
    ) -> None:
        self.id: Final = _id
        self.document_id: Final = document_id
        self.thread_id: Final = thread_id
        self.used_at = used_at
        self.created_at: Final = created_at
        self.updated_at = updated_at

    @classmethod
    def new(
            cls,
            _id: OpenaiAssistantId,
            document_id: DocumentId,
            thread_id: OpenaiThreadId,
            now: datetime,
    ) -> OpenaiAssistant:
        return cls(
            _id,
            document_id,
            thread_id,
            now,
            now,
            now,
        )

    def use(self, now: datetime) -> None:
        self.used_at = now
        self.updated_at = now


@final
class OpenaiMessage:
    def __init__(
            self,
            _id: OpenaiMessageId,
            thread_id: OpenaiThreadId,
            role: Literal["user", "assistant"],
            message: str,
            created_at: datetime,
    ) -> None:
        self.id: Final = _id
        self.thread_id: Final = thread_id
        self.role: Final = role
        self.message: Final = message
        self.created_at: Final = created_at

    @classmethod
    def new(
            cls,
            thread_id: OpenaiThreadId,
            role: Literal["user", "assistant"],
            message: str,
            now: datetime,
    ) -> OpenaiMessage:
        return cls(
            OpenaiMessageId(str(uuid.uuid4())),
            thread_id,
            role,
            message,
            now,
        )
