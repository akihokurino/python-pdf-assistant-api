from __future__ import annotations

from enum import Enum
from typing import final, Tuple

from flask import jsonify, Response


@final
class AppError(Exception):
    """アプリケーションエラー"""

    def __init__(self, kind: ErrorKind, message: str = "エラーが発生しました") -> None:
        self.kind = kind
        self.message = message
        super().__init__(message)

    def error_response(self) -> Tuple[Response, int]:
        return (
            jsonify({"message": self.message, "code": self.kind.value}),
            self.kind.value,
        )


@final
class ErrorKind(Enum):
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    NOT_FOUND = 404
    INTERNAL = 500
