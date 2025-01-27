from typing import final, Final

from google.cloud.firestore import AsyncClient

from adapter.adapter import AssistantFSRepository
from domain.assistant import Assistant, AssistantId
from domain.error import AppError, ErrorKind
from infra.firestore.entity import assistant_entity_from, ASSISTANT_KIND
from infra.firestore.util import delete_sub_collections


@final
class AssistantFSRepoImpl(AssistantFSRepository):
    def __init__(self, db: AsyncClient) -> None:
        self.db: Final = db

    @classmethod
    def new(cls, db: AsyncClient) -> AssistantFSRepository:
        return cls(db)

    async def put(self, assistant: Assistant) -> None:
        try:
            doc_ref = self.db.collection(ASSISTANT_KIND).document(assistant.id)
            await doc_ref.set(assistant_entity_from(assistant))
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL) from e

    async def delete(self, _id: AssistantId) -> None:
        try:
            doc_ref = self.db.collection(ASSISTANT_KIND).document(_id)
            await delete_sub_collections(doc_ref)
            await doc_ref.delete()
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL) from e
