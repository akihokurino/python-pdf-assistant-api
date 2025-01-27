from typing import final, Final

from google.cloud.firestore import AsyncClient

from adapter.adapter import AssistantFSRepository
from infra.firestore.util import delete_sub_collections
from domain.assistant import Assistant, AssistantId
from domain.error import AppError, ErrorKind


@final
class AssistantFSRepoImpl(AssistantFSRepository):
    def __init__(self, db: AsyncClient) -> None:
        self.db: Final = db

    @classmethod
    def new(cls, db: AsyncClient) -> AssistantFSRepository:
        return cls(db)

    async def put(self, item: Assistant) -> None:
        try:
            doc_ref = self.db.collection("Assistant").document(item.id)
            await doc_ref.set(
                {"id": item.id, "created_at": item.created_at.isoformat()}
            )
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, "データの保存に失敗しました。") from e

    async def delete(self, _id: AssistantId) -> None:
        try:
            doc_ref = self.db.collection("Assistant").document(_id)
            await delete_sub_collections(doc_ref)
            await doc_ref.delete()
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, "データの削除に失敗しました。") from e
