from typing import final, Final

from google.cloud.firestore import AsyncClient

from adapter.adapter import OpenaiMessageFSRepository
from model.error import AppError, ErrorKind
from model.openai_assistant import OpenaiMessage, OpenaiAssistant


@final
class OpenaiMessageFSRepoImpl(OpenaiMessageFSRepository):
    def __init__(self, db: AsyncClient) -> None:
        self.db: Final = db

    @classmethod
    def new(cls, db: AsyncClient) -> OpenaiMessageFSRepository:
        return cls(db)

    async def put(self, assistant: OpenaiAssistant, item: OpenaiMessage) -> None:
        try:
            parent_doc_ref = self.db.collection("OpenaiAssistant").document(assistant.id)
            doc_ref = parent_doc_ref.collection("OpenaiMessage").document(item.id)
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
