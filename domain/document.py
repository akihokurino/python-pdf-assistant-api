from __future__ import annotations

import dataclasses
import uuid
from datetime import datetime
from enum import Enum
from typing import final, NewType, Self

from domain.user import UserId

DocumentId = NewType("DocumentId", str)
DocumentSummaryId = NewType("DocumentSummaryId", str)


@final
@dataclasses.dataclass
class Document:
    id: DocumentId
    user_id: UserId
    name: str
    description: str
    gs_file_url: str
    status: Status
    created_at: datetime
    updated_at: datetime

    @classmethod
    def new(
            cls,
            user_id: UserId,
            name: str,
            description: str,
            gs_file_url: str,
            now: datetime,
    ) -> Self:
        return cls(
            id=DocumentId(str(uuid.uuid4())),
            user_id=user_id,
            name=name,
            description=description,
            gs_file_url=gs_file_url,
            status=Status.PREPARE_ASSISTANT,
            created_at=now,
            updated_at=now,
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


@final
@dataclasses.dataclass
class DocumentSummary:
    id: DocumentSummaryId
    document_id: DocumentId
    text: str
    index: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def new(
            cls, document_id: DocumentId, text: str, index: int, now: datetime
    ) -> Self:
        return cls(
            id=DocumentSummaryId(str(uuid.uuid4())),
            document_id=document_id,
            text=text,
            index=index,
            created_at=now,
            updated_at=now,
        )
