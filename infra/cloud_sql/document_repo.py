from typing import Optional, final, Final

from sqlalchemy import and_, desc
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from adapter.adapter import DocumentRepository, Pager
from domain.assistant import Assistant
from domain.document import Document, DocumentId
from domain.error import ErrorKind, AppError
from domain.user import UserId, User
from infra.cloud_sql.cursor import decode_cursor, encode_cursor, paging_result
from infra.cloud_sql.entity import (
    DocumentEntity,
    document_from,
    document_entity_from,
    user_from,
    AssistantEntity,
    assistant_from,
)


@final
class DocumentRepoImpl:
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

    async def find_by_user(
            self, user_id: UserId, limit: Optional[int] = None
    ) -> list[Document]:
        try:
            async with self.session() as session:
                query = select(DocumentEntity).filter_by(user_id=user_id)
                if limit:
                    query = query.limit(limit)
                entities = (await session.execute(query)).scalars().all()
                return [document_from(e) for e in entities]
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL) from e

    async def find_by_user_with_pager(
            self, user_id: UserId, pager: Pager
    ) -> tuple[list[Document], str]:
        try:
            async with self.session() as session:
                pager_params = decode_cursor(pager.cursor)
                query = (
                    select(DocumentEntity)
                    .filter_by(user_id=user_id)
                    .order_by(desc(DocumentEntity.created_at), desc(DocumentEntity.id))
                )
                if pager_params:
                    sk, pk = pager_params
                    query = query.where(
                        and_(
                            (DocumentEntity.created_at < sk)
                            | (
                                    (DocumentEntity.created_at == sk)
                                    & (DocumentEntity.id < pk)
                            )
                        )
                    )

                query = query.limit(pager.limit_with_next_one())
                entities = (await session.execute(query)).scalars().all()
                return paging_result(
                    pager,
                    entities,
                    document_from,
                    lambda v: encode_cursor(v.created_at, v.id),
                )
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
                    (await session.execute(select(DocumentEntity).filter_by(id=_id)))
                    .scalars()
                    .one_or_none()
                )
                if not document_entity:
                    raise AppError(ErrorKind.NOT_FOUND)
                await session.delete(document_entity)

                await session.commit()
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL) from e
