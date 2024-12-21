from model.user import User


def user_resp(user: User) -> dict[str, str | int]:
    return {
        "id": user.id,
        "name": user.name,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat(),
    }
