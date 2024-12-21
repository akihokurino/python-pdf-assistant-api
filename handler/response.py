from typing import Any

from model.user import User


def user_response(user: User) -> dict[str, Any]:
    return {
        "id": user.id,
        "name": user.name,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat(),
    }
