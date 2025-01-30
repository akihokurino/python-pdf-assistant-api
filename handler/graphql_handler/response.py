from __future__ import annotations

from datetime import datetime

import strawberry

from domain.user import User


@strawberry.type  # type: ignore
class MeResp:
    id: str
    name: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, user: User) -> MeResp:
        return cls(
            id=user.id,
            name=user.name,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
