from __future__ import annotations

import dataclasses
import uuid
from datetime import datetime
from typing import final, NewType, Literal, TypeAlias

from domain.document import DocumentId

AssistantId = NewType("AssistantId", str)
ThreadId = NewType("ThreadId", str)
MessageId = NewType("MessageId", str)


@final
@dataclasses.dataclass
class Assistant:
    id: AssistantId
    document_id: DocumentId
    thread_id: ThreadId
    used_at: datetime
    created_at: datetime
    updated_at: datetime

    @classmethod
    def new(
            cls,
            _id: AssistantId,
            document_id: DocumentId,
            thread_id: ThreadId,
            now: datetime,
    ) -> Assistant:
        return cls(
            id=_id,
            document_id=document_id,
            thread_id=thread_id,
            used_at=now,
            created_at=now,
            updated_at=now,
        )

    def use(self, now: datetime) -> None:
        self.used_at = now
        self.updated_at = now


@final
@dataclasses.dataclass
class Message:
    id: MessageId
    thread_id: ThreadId
    role: MessageRole
    message: str
    created_at: datetime

    @classmethod
    def new(
            cls,
            thread_id: ThreadId,
            role: MessageRole,
            message: str,
            now: datetime,
    ) -> Message:
        return cls(
            id=MessageId(str(uuid.uuid4())),
            thread_id=thread_id,
            role=role,
            message=message,
            created_at=now,
        )


MessageRole: TypeAlias = Literal["user", "assistant"]
