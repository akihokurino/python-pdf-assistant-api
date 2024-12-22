from model.document import Document
from model.user import User


def user_resp(user: User) -> dict[str, str | int]:
    return {
        "id": user.id,
        "name": user.name,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat(),
    }


def document_resp(document: Document) -> dict[str, str | int]:
    return {
        "id": document.id,
        "user_id": document.user_id,
        "name": document.name,
        "description": document.description,
        "gs_file_url": document.gs_file_url,
        "status": document.status.value,
        "created_at": document.created_at.isoformat(),
        "updated_at": document.updated_at.isoformat(),
    }
