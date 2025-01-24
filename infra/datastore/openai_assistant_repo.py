from typing import final

from google.cloud.firestore import AsyncClient

from adapter.adapter import OpenaiAssistantFSRepository
from model.error import AppError, ErrorKind
from model.openai_assistant import OpenaiAssistant, OpenaiAssistantId

KIND = "OpenaiAssistant"


@final
class OpenaiAssistantFSRepoImpl(OpenaiAssistantFSRepository):
    def __init__(self, db: AsyncClient) -> None:
        self.db = db

    @classmethod
    def new(cls, db: AsyncClient) -> OpenaiAssistantFSRepository:
        return cls(db)

    async def put(self, item: OpenaiAssistant) -> None:
        try:
            doc_ref = self.db.collection(KIND).document(item.id)
            await doc_ref.set({
                "id": item.id,
                "created_at": item.created_at.isoformat()
            })
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, "データの保存に失敗しました。") from e

    async def delete(self, _id: OpenaiAssistantId) -> None:
        try:
            doc_ref = self.db.collection(KIND).document(_id)
            await doc_ref.delete()
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, "データの削除に失敗しました。") from e
