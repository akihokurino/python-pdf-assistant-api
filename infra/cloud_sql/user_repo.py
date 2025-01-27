from typing import Optional, final, Final

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from adapter.adapter import UserRepository
from domain.document import Document
from domain.error import AppError, ErrorKind
from domain.user import User, UserId
from infra.cloud_sql.entity import (
    UserEntity,
    user_from,
    user_entity_from,
    document_from,
)


@final
class UserRepoImpl(UserRepository):
    def __init__(
            self,
            session: async_sessionmaker[AsyncSession],
    ) -> None:
        self.session: Final = session

    @classmethod
    def new(
            cls,
            session: async_sessionmaker[AsyncSession],
    ) -> UserRepository:
        return cls(session)

    async def find(self) -> list[User]:
        try:
            async with self.session() as session:
                result = await session.execute(select(UserEntity))
                entities = result.scalars().all()
                return [user_from(e) for e in entities]
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, f"ユーザーの取得に失敗しました。") from e

    async def get(self, _id: UserId) -> Optional[User]:
        try:
            async with self.session() as session:
                result = await session.execute(select(UserEntity).filter_by(id=_id))
                entity = result.scalars().one_or_none()
                if not entity:
                    return None
                return user_from(entity)
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, f"ユーザーの取得に失敗しました。") from e

    async def get_with_documents(
            self, _id: UserId
    ) -> Optional[tuple[User, list[Document]]]:
        try:
            async with self.session() as session:
                result = await session.execute(
                    select(UserEntity)
                    .filter_by(id=_id)
                    .options(selectinload(UserEntity.documents))
                )
                entity = result.scalars().one_or_none()
                if not entity:
                    return None
                return user_from(entity), [document_from(e) for e in entity.documents]
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, f"ユーザーの取得に失敗しました。") from e

    async def insert(self, item: User) -> None:
        try:
            async with self.session() as session:
                entity = user_entity_from(item)
                session.add(entity)
                await session.commit()
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, f"ユーザーの登録に失敗しました。") from e

    async def update(self, item: User) -> None:
        try:
            async with self.session() as session:
                result = await session.execute(select(UserEntity).filter_by(id=item.id))
                entity = result.scalars().one_or_none()
                if not entity:
                    raise AppError(
                        ErrorKind.NOT_FOUND, f"ユーザーが見つかりません: {item.id}"
                    )
                entity.update(item)
                await session.commit()
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, f"ユーザーの更新に失敗しました。") from e

    async def delete(self, _id: UserId) -> None:
        try:
            async with self.session() as session:
                result = await session.execute(select(UserEntity).filter_by(id=_id))
                entity = result.scalars().one_or_none()
                if not entity:
                    raise AppError(
                        ErrorKind.NOT_FOUND, f"ユーザーが見つかりません: {_id}"
                    )
                await session.delete(entity)
                await session.commit()
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, f"ユーザーの削除に失敗しました。") from e
