from datetime import datetime
from typing import Optional, final, Final

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from adapter.adapter import AssistantRepository
from domain.assistant import Assistant
from domain.document import DocumentId, Document
from domain.error import AppError, ErrorKind
from infra.cloud_sql.entity import (
    assistant_entity_from,
    assistant_from,
    AssistantEntity,
    document_from,
    DocumentEntity,
)


@final
class AssistantRepoImpl:
    def __init__(
        self,
        session: async_sessionmaker[AsyncSession],
    ) -> None:
        self.session: Final = session

    @classmethod
    def new(
        cls,
        session: async_sessionmaker[AsyncSession],
    ) -> AssistantRepository:
        return cls(session)

    async def find_past(
        self,
        date: datetime,
    ) -> list[tuple[Assistant, Document]]:
        try:
            async with self.session() as session:
                entities = (
                    (
                        await session.execute(
                            select(AssistantEntity)
                            .filter(AssistantEntity.used_at < date)
                            .options(selectinload(AssistantEntity.document))
                        )
                    )
                    .scalars()
                    .all()
                )
                return [
                    (assistant_from(e), document_from(e.document)) for e in entities
                ]
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL) from e

    async def get(self, _id: DocumentId) -> Optional[Assistant]:
        try:
            async with self.session() as session:
                entity = (
                    (
                        await session.execute(
                            select(AssistantEntity).filter_by(document_id=_id)
                        )
                    )
                    .scalars()
                    .one_or_none()
                )
                if not entity:
                    return None
                return assistant_from(entity)
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL) from e

    async def insert(self, assistant: Assistant) -> None:
        try:
            async with self.session() as session:
                entity = assistant_entity_from(assistant)
                session.add(entity)
                await session.commit()
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL) from e

    async def insert_with_update_document(
        self, assistant: Assistant, document: Document
    ) -> None:
        try:
            async with self.session() as session:
                assistant_entity = assistant_entity_from(assistant)
                session.add(assistant_entity)

                document_entity = (
                    (
                        await session.execute(
                            select(DocumentEntity).filter_by(id=document.id)
                        )
                    )
                    .scalars()
                    .one_or_none()
                )
                if not document_entity:
                    raise AppError(ErrorKind.NOT_FOUND)
                document_entity.update(document)

                await session.commit()
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL) from e

    async def update(self, assistant: Assistant) -> None:
        try:
            async with self.session() as session:
                entity = (
                    (
                        await session.execute(
                            select(AssistantEntity).filter_by(
                                document_id=assistant.document_id
                            )
                        )
                    )
                    .scalars()
                    .one_or_none()
                )
                if not entity:
                    raise AppError(ErrorKind.NOT_FOUND)
                entity.update(assistant)
                await session.commit()
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL) from e

    async def delete(self, _id: DocumentId) -> None:
        try:
            async with self.session() as session:
                entity = (
                    (
                        await session.execute(
                            select(AssistantEntity).filter_by(document_id=_id)
                        )
                    )
                    .scalars()
                    .one_or_none()
                )
                if not entity:
                    raise AppError(ErrorKind.NOT_FOUND)
                await session.delete(entity)
                await session.commit()
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL) from e

    async def delete_with_update_document(
        self, _id: DocumentId, document: Document
    ) -> None:
        try:
            async with self.session() as session:
                assistant_entity = (
                    (
                        await session.execute(
                            select(AssistantEntity).filter_by(document_id=_id)
                        )
                    )
                    .scalars()
                    .one_or_none()
                )
                if not assistant_entity:
                    raise AppError(ErrorKind.NOT_FOUND)
                await session.delete(assistant_entity)

                document_entity = (
                    (
                        await session.execute(
                            select(DocumentEntity).filter_by(id=document.id)
                        )
                    )
                    .scalars()
                    .one_or_none()
                )
                if not document_entity:
                    raise AppError(ErrorKind.NOT_FOUND)
                document_entity.update(document)

                await session.commit()
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL) from e
