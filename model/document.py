from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import final, NewType

from model.user import UserId

DocumentId = NewType("DocumentId", str)


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
        self.status: Status = status
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

    def update_status(self, status: Status, now: datetime) -> None:
        self.status = status
        self.updated_at = now


@final
class Status(Enum):
    PREPARE_ASSISTANT = 1
    READY_ASSISTANT = 2
