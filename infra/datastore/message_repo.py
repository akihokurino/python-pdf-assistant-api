from typing import final, Final

from google.cloud.firestore import AsyncClient

from adapter.adapter import MessageFSRepository
from model.assistant import Message, Assistant
from model.error import AppError, ErrorKind


@final
class MessageFSRepoImpl(MessageFSRepository):
    def __init__(self, db: AsyncClient) -> None:
        self.db: Final = db

    @classmethod
    def new(cls, db: AsyncClient) -> MessageFSRepository:
        return cls(db)

    async def put(self, assistant: Assistant, item: Message) -> None:
        try:
            parent_doc_ref = self.db.collection("Assistant").document(assistant.id)
            doc_ref = parent_doc_ref.collection("Message").document(item.id)
            await doc_ref.set(
                {
                    "id": item.id,
                    "thread_id": item.thread_id,
                    "role": item.role,
                    "message": item.message,
                    "created_at": item.created_at.isoformat()}
            )
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, "データの保存に失敗しました。") from e
