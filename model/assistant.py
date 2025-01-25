from __future__ import annotations

import uuid
from datetime import datetime
from typing import final, NewType, Final, Literal

from model.document import DocumentId

AssistantId = NewType("AssistantId", str)
ThreadId = NewType("ThreadId", str)
MessageId = NewType("MessageId", str)


@final
class Assistant:
    def __init__(
            self,
            _id: AssistantId,
            document_id: DocumentId,
            thread_id: ThreadId,
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
            _id: AssistantId,
            document_id: DocumentId,
            thread_id: ThreadId,
            now: datetime,
    ) -> Assistant:
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
class Message:
    def __init__(
            self,
            _id: MessageId,
            thread_id: ThreadId,
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
            thread_id: ThreadId,
            role: Literal["user", "assistant"],
            message: str,
            now: datetime,
    ) -> Message:
        return cls(
            MessageId(str(uuid.uuid4())),
            thread_id,
            role,
            message,
            now,
        )
