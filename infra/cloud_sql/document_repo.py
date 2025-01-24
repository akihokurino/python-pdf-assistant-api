from typing import Optional, List, Tuple, final

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from adapter.adapter import DocumentRepository
from infra.cloud_sql.entity import (
    DocumentEntity,
    document_from,
    document_entity_from,
    user_from,
    OpenaiAssistantEntity,
)
from model.document import Document, DocumentId
from model.error import ErrorKind, AppError
from model.user import UserId, User


@final
class DocumentRepoImpl(DocumentRepository):
    def __init__(
            self,
            session: async_sessionmaker[AsyncSession],
    ) -> None:
        self.session = session

    @classmethod
    def new(
            cls,
            session: async_sessionmaker[AsyncSession],
    ) -> DocumentRepository:
        return cls(session)

    async def find_by_user(self, user_id: UserId) -> List[Document]:
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
            raise AppError(
                ErrorKind.INTERNAL, f"ドキュメントの取得に失敗しました。"
            ) from e

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
            raise AppError(
                ErrorKind.INTERNAL, f"ドキュメントの取得に失敗しました。"
            ) from e

    async def get_with_user(
            self, _id: DocumentId
    ) -> Optional[Tuple[Document, User]]:
        try:
            async with self.session() as session:
                entity = (
                    (
                        await session.execute(
                            select(DocumentEntity)
                            .filter_by(id=_id)
                            .options(selectinload(DocumentEntity.user))
                        )
                    )
                    .scalars()
                    .one_or_none()
                )
                if not entity:
                    return None
                return document_from(entity), user_from(entity.user)
        except Exception as e:
            raise AppError(
                ErrorKind.INTERNAL, f"ドキュメントの取得に失敗しました。"
            ) from e

    async def insert(self, item: Document) -> None:
        try:
            async with self.session() as session:
                entity = document_entity_from(item)
                session.add(entity)
                await session.commit()
        except Exception as e:
            raise AppError(
                ErrorKind.INTERNAL, f"ドキュメントの登録に失敗しました。"
            ) from e

    async def update(self, item: Document) -> None:
        try:
            async with self.session() as session:
                entity = (
                    (
                        await session.execute(
                            select(DocumentEntity).filter_by(id=item.id)
                        )
                    )
                    .scalars()
                    .one_or_none()
                )
                if not entity:
                    raise AppError(
                        ErrorKind.NOT_FOUND, f"ドキュメントが見つかりません: {item.id}"
                    )
                entity.update(item)
                await session.commit()
        except Exception as e:
            raise AppError(
                ErrorKind.INTERNAL, f"ドキュメントの更新に失敗しました。"
            ) from e

    async def delete(self, _id: DocumentId) -> None:
        try:
            async with self.session() as session:
                entity = (
                    (await session.execute(select(DocumentEntity).filter_by(id=_id)))
                    .scalars()
                    .one_or_none()
                )
                if not entity:
                    raise AppError(
                        ErrorKind.NOT_FOUND, f"ドキュメントが見つかりません: {_id}"
                    )
                await session.delete(entity)
                await session.commit()
        except Exception as e:
            raise AppError(
                ErrorKind.INTERNAL, f"ドキュメントの削除に失敗しました。"
            ) from e

    async def delete_with_assistant(self, _id: DocumentId) -> None:
        try:
            async with self.session() as session:
                entity1 = (
                    (
                        await session.execute(
                            select(OpenaiAssistantEntity).filter_by(document_id=_id)
                        )
                    )
                    .scalars()
                    .one_or_none()
                )
                if entity1 is not None:
                    await session.delete(entity1)

                entity2 = (
                    (await session.execute(select(DocumentEntity).filter_by(id=_id)))
                    .scalars()
                    .one_or_none()
                )
                if not entity2:
                    raise AppError(
                        ErrorKind.NOT_FOUND,
                        f"ドキュメントが見つかりません: {_id}",
                    )
                await session.delete(entity2)

                await session.commit()
        except Exception as e:
            raise AppError(
                ErrorKind.INTERNAL, f"アシスタント/ドキュメントの削除に失敗しました。"
            ) from e
