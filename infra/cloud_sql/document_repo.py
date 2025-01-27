from typing import Optional, final, Final

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from adapter.adapter import DocumentRepository
from domain.assistant import Assistant
from domain.document import Document, DocumentId
from domain.error import ErrorKind, AppError
from domain.user import UserId, User
from infra.cloud_sql.entity import (
    DocumentEntity,
    document_from,
    document_entity_from,
    user_from,
    AssistantEntity,
    assistant_from,
)


@final
class DocumentRepoImpl(DocumentRepository):
    def __init__(
            self,
            session: async_sessionmaker[AsyncSession],
    ) -> None:
        self.session: Final = session

    @classmethod
    def new(
            cls,
            session: async_sessionmaker[AsyncSession],
    ) -> DocumentRepository:
        return cls(session)

    async def find_by_user(self, user_id: UserId) -> list[Document]:
        try:
            async with self.session() as session:
                entities = (
                    (
                        await session.execute(
                            select(DocumentEntity).filter_by(user_id=user_id)
                        )
                    )
                    .scalars()
                    .all()
                )
                return [document_from(e) for e in entities]
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL) from e

    async def get(self, _id: DocumentId) -> Optional[Document]:
        try:
            async with self.session() as session:
                entity = (
                    (await session.execute(select(DocumentEntity).filter_by(id=_id)))
                    .scalars()
                    .one_or_none()
                )
                if not entity:
                    return None
                return document_from(entity)
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL) from e

    async def get_with_user_and_assistant(
            self, _id: DocumentId
    ) -> Optional[tuple[Document, User, Optional[Assistant]]]:
        try:
            async with self.session() as session:
                entity = (
                    (
                        await session.execute(
                            select(DocumentEntity)
                            .filter_by(id=_id)
                            .options(
                                selectinload(DocumentEntity.user),
                                selectinload(DocumentEntity.assistant),
                            )
                        )
                    )
                    .scalars()
                    .one_or_none()
                )
                if not entity:
                    return None
                return (
                    document_from(entity),
                    user_from(entity.user),
                    assistant_from(entity.assistant) if entity.assistant else None,
                )
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL) from e

    async def insert(self, document: Document) -> None:
        try:
            async with self.session() as session:
                entity = document_entity_from(document)
                session.add(entity)
                await session.commit()
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL) from e

    async def update(self, document: Document) -> None:
        try:
            async with self.session() as session:
                entity = (
                    (
                        await session.execute(
                            select(DocumentEntity).filter_by(id=document.id)
                        )
                    )
                    .scalars()
                    .one_or_none()
                )
                if not entity:
                    raise AppError(ErrorKind.NOT_FOUND)
                entity.update(document)
                await session.commit()
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL) from e

    async def delete(self, _id: DocumentId) -> None:
        try:
            async with self.session() as session:
                entity = (
                    (await session.execute(select(DocumentEntity).filter_by(id=_id)))
                    .scalars()
                    .one_or_none()
                )
                if not entity:
                    raise AppError(ErrorKind.NOT_FOUND)
                await session.delete(entity)
                await session.commit()
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL) from e

    async def delete_with_assistant(self, _id: DocumentId) -> None:
        try:
            async with self.session() as session:
                entity1 = (
                    (
                        await session.execute(
                            select(AssistantEntity).filter_by(document_id=_id)
                        )
                    )
                    .scalars()
                    .one_or_none()
                )
                if not entity1:
                    raise AppError(ErrorKind.NOT_FOUND)
                await session.delete(entity1)

                entity2 = (
                    (await session.execute(select(DocumentEntity).filter_by(id=_id)))
                    .scalars()
                    .one_or_none()
                )
                if not entity2:
                    raise AppError(ErrorKind.NOT_FOUND)
                await session.delete(entity2)

                await session.commit()
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL) from e
