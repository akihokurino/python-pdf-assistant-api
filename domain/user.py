from __future__ import annotations

import dataclasses
from datetime import datetime
from typing import final, NewType

UserId = NewType("UserId", str)


@final
@dataclasses.dataclass
class User:
    id: UserId
    name: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def new(cls, _id: UserId, name: str, now: datetime) -> User:
        return cls(id=_id, name=name, created_at=now, updated_at=now)

    def update(self, name: str, now: datetime) -> None:
        self.name = name
        self.updated_at = now
