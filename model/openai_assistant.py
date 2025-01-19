from __future__ import annotations

from datetime import datetime
from typing import final, NewType

from model.document import DocumentId

OpenaiAssistantId = NewType("OpenaiAssistantId", str)
OpenaiThreadId = NewType("OpenaiThreadId", str)


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
        self.id = _id
        self.document_id = document_id
        self.thread_id = thread_id
        self.used_at = used_at
        self.created_at = created_at
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
