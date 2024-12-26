from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import final, NewType

from model.user import UserId

DocumentId = NewType("DocumentId", str)
OpenaiAssistantId = NewType("OpenaiAssistantId", str)
OpenaiThreadId = NewType("OpenaiThreadId", str)


@final
class Document:
    def __init__(
        self,
        _id: DocumentId,
        user_id: UserId,
        name: str,
        description: str,
        gs_file_url: str,
        status: Status,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        self.id = _id
        self.user_id = user_id
        self.name = name
        self.description = description
        self.gs_file_url = gs_file_url
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def new(
        cls,
        user_id: UserId,
        name: str,
        description: str,
        gs_file_url: str,
        now: datetime,
    ) -> Document:
        return cls(
            DocumentId(str(uuid.uuid4())),
            user_id,
            name,
            description,
            gs_file_url,
            Status.PREPARE_ASSISTANT,
            now,
            now,
        )

    def update(self, name: str, description: str, now: datetime) -> None:
        self.name = name
        self.description = description
        self.updated_at = now


@final
class Status(Enum):
    PREPARE_ASSISTANT = 1


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
