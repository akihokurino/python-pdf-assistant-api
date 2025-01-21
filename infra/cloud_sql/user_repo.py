from typing import Optional, List, Tuple, Any

from sqlalchemy.orm import joinedload
from sqlalchemy.orm import sessionmaker, Session as OrmSession

from adapter.adapter import UserRepository
from infra.cloud_sql.entity import (
    UserEntity,
    user_from,
    user_entity_from,
    document_from,
)
from model.document import Document
from model.error import AppError, ErrorKind
from model.user import User, UserId


class UserRepoImpl(UserRepository):
    def __init__(
            self,
            session: Any,
    ) -> None:
        self.session = session

    @classmethod
    def new(
            cls,
            session: sessionmaker[OrmSession],
    ) -> UserRepository:
        return cls(session)

    def find_users(self) -> List[User]:
        try:
            with self.session() as session:
                entities = session.query(UserEntity).all()
                return [user_from(e) for e in entities]
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, f"ユーザーの取得に失敗しました。") from e

    def get_user(self, _id: UserId) -> Optional[User]:
        try:
            with self.session() as session:
                entity = session.query(UserEntity).filter_by(id=_id).one_or_none()
                if not entity:
                    return None
                return user_from(entity)
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, f"ユーザーの取得に失敗しました。") from e

    def get_user_with_documents(self, _id: UserId) -> Optional[Tuple[User, List[Document]]]:
        try:
            with self.session() as session:
                entity = (
                    session.query(UserEntity)
                    .filter_by(id=_id)
                    .options(joinedload(UserEntity.documents))
                    .one_or_none()
                )
                if not entity:
                    return None
                return user_from(entity), [document_from(e) for e in entity.documents]
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, f"ユーザーの取得に失敗しました。") from e

    def insert_user(self, item: User) -> None:
        try:
            with self.session() as session:
                entity = user_entity_from(item)
                session.add(entity)
                session.commit()
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, f"ユーザーの登録に失敗しました。") from e

    def update_user(self, item: User) -> None:
        try:
            with self.session() as session:
                entity = session.query(UserEntity).filter_by(id=item.id).one_or_none()
                if not entity:
                    raise AppError(ErrorKind.NOT_FOUND, f"ユーザーが見つかりません: {item.id}")
                entity.update(item)
                session.commit()
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, f"ユーザーの更新に失敗しました。") from e

    def delete_user(self, _id: UserId) -> None:
        try:
            with self.session() as session:
                entity = session.query(UserEntity).filter_by(id=_id).one_or_none()
                if not entity:
                    raise AppError(ErrorKind.NOT_FOUND, f"ユーザーが見つかりません: {_id}")
                session.delete(entity)
                session.commit()
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, f"ユーザーの削除に失敗しました。") from e
