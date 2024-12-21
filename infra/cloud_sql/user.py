from datetime import datetime
from typing import Optional, List, final

from sqlalchemy import Column, String, DateTime

from infra.cloud_sql.common import Base, Session
from model.error import AppError, ErrorKind
from model.user import User


@final
class UserEntity(Base):
    __tablename__ = "users"

    id: str = Column(String(255), primary_key=True)
    name: str = Column(String(255), nullable=False)
    created_at: datetime = Column(DateTime, nullable=False)
    updated_at: datetime = Column(DateTime, nullable=False)

    def update(self, user: User) -> None:
        self.name = user.name
        self.updated_at = user.updated_at


def _entity_from(u: User) -> UserEntity:
    return UserEntity(
        id=u.id,
        name=u.name,
        created_at=u.created_at,
        updated_at=u.updated_at,
    )


def _user_from(u: UserEntity) -> User:
    return User(
        _id=u.id,
        name=u.name,
        created_at=u.created_at,
        updated_at=u.updated_at,
    )


def find_users() -> List[User]:
    session = Session()
    try:
        entities = session.query(UserEntity).all()
        return [_user_from(e) for e in entities]
    except Exception as e:
        raise AppError(ErrorKind.INTERNAL, f"ユーザーの取得に失敗しました。") from e
    finally:
        session.close()


def get_user(_id: str) -> Optional[User]:
    session = Session()
    try:
        entity = session.query(UserEntity).filter_by(id=_id).first()
        if not entity:
            return None
        return _user_from(entity)
    except Exception as e:
        raise AppError(ErrorKind.INTERNAL, f"ユーザーの取得に失敗しました。") from e
    finally:
        session.close()


def insert_user(user: User) -> None:
    session = Session()
    try:
        entity = _entity_from(user)
        session.add(entity)
        session.commit()
    except Exception as e:
        session.rollback()
        raise AppError(ErrorKind.INTERNAL, f"ユーザーの登録に失敗しました。") from e
    finally:
        session.close()


def update_user(user: User) -> None:
    session = Session()
    try:
        entity = session.query(UserEntity).filter_by(id=user.id).first()
        if not entity:
            raise AppError(ErrorKind.NOT_FOUND, f"ユーザーが見つかりません: {user.id}")
        entity.update(user)
        session.commit()
    except Exception as e:
        session.rollback()
        raise AppError(ErrorKind.INTERNAL, f"ユーザーの更新に失敗しました。") from e
    finally:
        session.close()


def delete_user(_id: str) -> None:
    session = Session()
    try:
        entity = session.query(UserEntity).filter_by(id=_id).first()
        if not entity:
            raise AppError(ErrorKind.NOT_FOUND, f"ユーザーが見つかりません: {_id}")
        session.delete(entity)
        session.commit()
    except Exception as e:
        session.rollback()
        raise AppError(ErrorKind.INTERNAL, f"ユーザーの削除に失敗しました。") from e
    finally:
        session.close()
