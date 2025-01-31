from __future__ import annotations

from datetime import datetime

import strawberry

from domain.document import Document


@strawberry.type  # type: ignore
class DocumentResp:
    id: str
    user_id: str
    name: str
    description: str
    gs_file_url: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, doc: Document) -> DocumentResp:
        return cls(
            id=doc.id,
            user_id=doc.user_id,
            name=doc.name,
            description=doc.description,
            gs_file_url=doc.gs_file_url,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
        )
