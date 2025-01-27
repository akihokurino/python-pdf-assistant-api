from typing import final, Final

from google.cloud.firestore import AsyncClient

from adapter.adapter import MessageFSRepository
from domain.assistant import Message, Assistant
from domain.error import AppError, ErrorKind
from infra.firestore.entity import (
    ASSISTANT_KIND,
    MESSAGE_KIND,
    message_entity_from,
    message_from,
)


@final
class MessageFSRepoImpl:
    def __init__(self, db: AsyncClient) -> None:
        self.db: Final = db

    @classmethod
    def new(cls, db: AsyncClient) -> MessageFSRepository:
        return cls(db)

    async def find(self, assistant: Assistant) -> list[Message]:
        try:
            parent_doc_ref = self.db.collection(ASSISTANT_KIND).document(assistant.id)
            docs = (
                parent_doc_ref.collection(MESSAGE_KIND)
                .order_by("created_at", direction="DESCENDING")
                .stream()
            )

            messages = [message_from(doc) async for doc in docs]

            return messages
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL) from e

    async def put(self, assistant: Assistant, message: Message) -> None:
        try:
            parent_doc_ref = self.db.collection(ASSISTANT_KIND).document(assistant.id)
            doc_ref = parent_doc_ref.collection(MESSAGE_KIND).document(message.id)
            await doc_ref.set(message_entity_from(message))
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL) from e
