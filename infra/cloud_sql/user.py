from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, DateTime

from infra.cloud_sql.common import Base, Session
from model.error import AppError, ErrorKind
from model.user import User


class UserEntity(Base):
    __tablename__ = "users"

    id: str = Column(String(255), primary_key=True)
    name: str = Column(String(255), nullable=False)
    created_at: datetime = Column(DateTime, nullable=False)


def get_user(_id: str) -> Optional[User]:
    session = Session()
    try:
        entity = session.query(UserEntity).filter_by(id=_id).first()
        if not entity:
            return None
        return User(entity.id, entity.name, entity.created_at)
    except Exception as e:
        raise AppError(ErrorKind.INTERNAL, f"ユーザーの取得に失敗しました。") from e
    finally:
        session.close()


def insert_user(user: User) -> None:
    session = Session()
    try:
        entity = UserEntity(id=user.id, name=user.name, created_at=user.created_at)
        session.add(entity)
        session.commit()
    except Exception as e:
        session.rollback()
        raise AppError(ErrorKind.INTERNAL, f"ユーザーの登録に失敗しました。") from e
    finally:
        session.close()
