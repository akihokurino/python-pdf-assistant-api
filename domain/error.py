from __future__ import annotations

from enum import Enum
from typing import final, Final


@final
class AppError(Exception):
    def __init__(self, kind: ErrorKind, message: str = "エラーが発生しました") -> None:
        self.kind: Final = kind
        self.message: Final = message
        super().__init__(message)

    def dict(self) -> dict[str, str | int]:
        return {"message": self.message, "code": self.kind.value}


@final
class ErrorKind(Enum):
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL = 500
