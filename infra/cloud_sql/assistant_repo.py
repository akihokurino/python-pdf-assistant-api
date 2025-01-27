from datetime import datetime
from typing import Optional, final, Final

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from adapter.adapter import AssistantRepository
from infra.cloud_sql.entity import (
    assistant_entity_from,
    assistant_from,
    AssistantEntity,
    document_from,
    DocumentEntity,
)
from model.assistant import Assistant
from model.document import DocumentId, Document
from model.error import AppError, ErrorKind


@final
class AssistantRepoImpl(AssistantRepository):
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
            raise AppError(ErrorKind.INTERNAL, f"データの取得に失敗しました。") from e

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
            raise AppError(
                ErrorKind.INTERNAL, f"アシスタントの取得に失敗しました。"
            ) from e

    async def insert(self, item: Assistant) -> None:
        try:
            async with self.session() as session:
                entity = assistant_entity_from(item)
                session.add(entity)
                await session.commit()
        except Exception as e:
            raise AppError(
                ErrorKind.INTERNAL, f"アシスタントの登録に失敗しました。"
            ) from e

    async def insert_with_update_document(
        self, assistant: Assistant, document: Document
    ) -> None:
        try:
            async with self.session() as session:
                entity1 = assistant_entity_from(assistant)
                session.add(entity1)

                entity2 = (
                    (
                        await session.execute(
                            select(DocumentEntity).filter_by(id=document.id)
                        )
                    )
                    .scalars()
                    .one_or_none()
                )
                if not entity2:
                    raise AppError(
                        ErrorKind.NOT_FOUND,
                        f"ドキュメントが見つかりません: {document.id}",
                    )
                entity2.update(document)

                await session.commit()
        except Exception as e:
            raise AppError(
                ErrorKind.INTERNAL, f"アシスタントの登録に失敗しました。"
            ) from e

    async def update(self, item: Assistant) -> None:
        try:
            async with self.session() as session:
                entity = (
                    (
                        await session.execute(
                            select(AssistantEntity).filter_by(
                                document_id=item.document_id
                            )
                        )
                    )
                    .scalars()
                    .one_or_none()
                )
                if not entity:
                    raise AppError(
                        ErrorKind.NOT_FOUND, f"アシスタントが見つかりません: {item.id}"
                    )
                entity.update(item)
                await session.commit()
        except Exception as e:
            raise AppError(
                ErrorKind.INTERNAL, f"アシスタントの更新に失敗しました。"
            ) from e

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
                    raise AppError(
                        ErrorKind.NOT_FOUND, f"アシスタントが見つかりません: {_id}"
                    )
                await session.delete(entity)
                await session.commit()
        except Exception as e:
            raise AppError(
                ErrorKind.INTERNAL, f"アシスタントの削除に失敗しました。"
            ) from e

    async def delete_with_update_document(
        self, _id: DocumentId, document: Document
    ) -> None:
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
                    raise AppError(
                        ErrorKind.NOT_FOUND, f"アシスタントが見つかりません: {_id}"
                    )
                await session.delete(entity1)

                entity2 = (
                    (
                        await session.execute(
                            select(DocumentEntity).filter_by(id=document.id)
                        )
                    )
                    .scalars()
                    .one_or_none()
                )
                if not entity2:
                    raise AppError(
                        ErrorKind.NOT_FOUND,
                        f"ドキュメントが見つかりません: {document.id}",
                    )
                entity2.update(document)

                await session.commit()
        except Exception as e:
            raise AppError(
                ErrorKind.INTERNAL, f"アシスタントの削除に失敗しました。"
            ) from e
