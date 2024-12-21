from __future__ import annotations

from datetime import datetime
from typing import final


@final
class User:
    def __init__(
        self, _id: str, name: str, created_at: datetime, updated_at: datetime
    ) -> None:
        self.id = _id
        self.name = name
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def new(cls, _id: str, name: str, now: datetime) -> User:
        return cls(_id, name, now, now)

    def update(self, name: str, now: datetime) -> None:
        self.name = name
        self.updated_at = now
