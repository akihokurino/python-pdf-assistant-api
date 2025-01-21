from typing import Optional, List, Tuple, Final

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
            session: sessionmaker[OrmSession],
    ) -> None:
        self.session: Final[sessionmaker[OrmSession]] = session

    @classmethod
    def new(
            cls,
            session: sessionmaker[OrmSession],
    ) -> UserRepository:
        return cls(session)

    def find_users(self) -> List[User]:
        session = self.session()
        try:
            entities = session.query(UserEntity).all()
            return [user_from(e) for e in entities]
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, f"ユーザーの取得に失敗しました。") from e
        finally:
            session.close()

    def get_user(self, _id: UserId) -> Optional[User]:
        session = self.session()
        try:
            entity = session.query(UserEntity).filter_by(id=_id).one_or_none()
            if not entity:
                return None
            return user_from(entity)
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, f"ユーザーの取得に失敗しました。") from e
        finally:
            session.close()

    def get_user_with_documents(self, _id: UserId) -> Optional[Tuple[User, List[Document]]]:
        session = self.session()
        try:
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
        finally:
            session.close()

    def insert_user(self, item: User) -> None:
        session = self.session()
        try:
            entity = user_entity_from(item)
            session.add(entity)
            session.commit()
        except Exception as e:
            session.rollback()
            raise AppError(ErrorKind.INTERNAL, f"ユーザーの登録に失敗しました。") from e
        finally:
            session.close()

    def update_user(self, item: User) -> None:
        session = self.session()
        try:
            entity = session.query(UserEntity).filter_by(id=item.id).one_or_none()
            if not entity:
                raise AppError(ErrorKind.NOT_FOUND, f"ユーザーが見つかりません: {item.id}")
            entity.update(item)
            session.commit()
        except Exception as e:
            session.rollback()
            raise AppError(ErrorKind.INTERNAL, f"ユーザーの更新に失敗しました。") from e
        finally:
            session.close()

    def delete_user(self, _id: UserId) -> None:
        session = self.session()
        try:
            entity = session.query(UserEntity).filter_by(id=_id).one_or_none()
            if not entity:
                raise AppError(ErrorKind.NOT_FOUND, f"ユーザーが見つかりません: {_id}")
            session.delete(entity)
            session.commit()
        except Exception as e:
            session.rollback()
            raise AppError(ErrorKind.INTERNAL, f"ユーザーの削除に失敗しました。") from e
        finally:
            session.close()
