from datetime import datetime
from typing import Optional, List, final

from sqlalchemy import Column, String, DateTime

from infra.cloud_sql.common import Base, Session
from model.error import AppError, ErrorKind
from model.user import User, UserId


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


def _entity_from(d: User) -> UserEntity:
    return UserEntity(
        id=d.id,
        name=d.name,
        created_at=d.created_at,
        updated_at=d.updated_at,
    )


def _domain_from(e: UserEntity) -> User:
    return User(
        _id=UserId(e.id),
        name=e.name,
        created_at=e.created_at,
        updated_at=e.updated_at,
    )


def find_users() -> List[User]:
    session = Session()
    try:
        entities = session.query(UserEntity).all()
        return [_domain_from(e) for e in entities]
    except Exception as e:
        raise AppError(ErrorKind.INTERNAL, f"ユーザーの取得に失敗しました。") from e
    finally:
        session.close()


def get_user(_id: UserId) -> Optional[User]:
    session = Session()
    try:
        entity = session.query(UserEntity).filter_by(id=_id).one_or_none()
        if not entity:
            return None
        return _domain_from(entity)
    except Exception as e:
        raise AppError(ErrorKind.INTERNAL, f"ユーザーの取得に失敗しました。") from e
    finally:
        session.close()


def insert_user(item: User) -> None:
    session = Session()
    try:
        entity = _entity_from(item)
        session.add(entity)
        session.commit()
    except Exception as e:
        session.rollback()
        raise AppError(ErrorKind.INTERNAL, f"ユーザーの登録に失敗しました。") from e
    finally:
        session.close()


def update_user(item: User) -> None:
    session = Session()
    try:
        entity = session.query(UserEntity).filter_by(id=item.id).first()
        if not entity:
            raise AppError(ErrorKind.NOT_FOUND, f"ユーザーが見つかりません: {item.id}")
        entity.update(item)
        session.commit()
    except Exception as e:
        session.rollback()
        raise AppError(ErrorKind.INTERNAL, f"ユーザーの更新に失敗しました。") from e
    finally:
        session.close()


def delete_user(_id: UserId) -> None:
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
