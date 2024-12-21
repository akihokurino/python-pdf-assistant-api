import json
from typing import Any, Tuple

from flask import Response

from model.user import User


def ok(data: dict[str, Any]) -> Tuple[Response, int]:
    json_data = json.dumps(data, ensure_ascii=False, indent=4)
    return Response(json_data, mimetype="application/json"), 200


def user_response(user: User) -> dict[str, Any]:
    return {
        "id": user.id,
        "name": user.name,
        "created_at": user.created_at.isoformat(),
    }
