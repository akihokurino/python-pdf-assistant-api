from datetime import datetime
from typing import final, Optional, List

from sqlalchemy import Column, String, DateTime, Integer

from infra.cloud_sql.common import Base, Session
from model.document import Document, DocumentId, Status
from model.error import ErrorKind, AppError
from model.user import UserId


@final
class DocumentEntity(Base):
    __tablename__ = "documents"

    id: str = Column(String(255), primary_key=True)
    user_id: str = Column(String(255), nullable=False)
    name: str = Column(String(255), nullable=False)
    description: str = Column(String(255), nullable=False)
    gs_file_url: str = Column(String(255), nullable=False)
    status: int = Column(Integer(), nullable=False)
    created_at: datetime = Column(DateTime, nullable=False)
    updated_at: datetime = Column(DateTime, nullable=False)

    def update(self, document: Document) -> None:
        self.name = document.name
        self.description = document.description
        self.gs_file_url = document.gs_file_url
        self.status = document.status.value
        self.updated_at = document.updated_at


def _entity_from(d: Document) -> DocumentEntity:
    return DocumentEntity(
        id=d.id,
        user_id=d.user_id,
        name=d.name,
        description=d.description,
        gs_file_url=d.gs_file_url,
        status=d.status.value,
        created_at=d.created_at,
        updated_at=d.updated_at,
    )


def _domain_from(e: DocumentEntity) -> Document:
    return Document(
        _id=DocumentId(e.id),
        user_id=UserId(e.user_id),
        name=e.name,
        description=e.description,
        gs_file_url=e.gs_file_url,
        status=Status(e.status),
        created_at=e.created_at,
        updated_at=e.updated_at,
    )


def find_documents_by_user(user_id: UserId) -> List[Document]:
    session = Session()
    try:
        entities = session.query(DocumentEntity).filter_by(user_id=user_id).all()
        return [_domain_from(e) for e in entities]
    except Exception as e:
        raise AppError(ErrorKind.INTERNAL, f"ドキュメントの取得に失敗しました。") from e
    finally:
        session.close()


def get_document(_id: DocumentId) -> Optional[Document]:
    session = Session()
    try:
        entity = session.query(DocumentEntity).filter_by(id=_id).one_or_none()
        if not entity:
            return None
        return _domain_from(entity)
    except Exception as e:
        raise AppError(ErrorKind.INTERNAL, f"ドキュメントの取得に失敗しました。") from e
    finally:
        session.close()


def insert_document(item: Document) -> None:
    session = Session()
    try:
        entity = _entity_from(item)
        session.add(entity)
        session.commit()
    except Exception as e:
        session.rollback()
        raise AppError(ErrorKind.INTERNAL, f"ドキュメントの登録に失敗しました。") from e
    finally:
        session.close()


def update_document(item: Document) -> None:
    session = Session()
    try:
        entity = session.query(DocumentEntity).filter_by(id=item.id).first()
        if not entity:
            raise AppError(
                ErrorKind.NOT_FOUND, f"ドキュメントが見つかりません: {item.id}"
            )
        entity.update(item)
        session.commit()
    except Exception as e:
        session.rollback()
        raise AppError(ErrorKind.INTERNAL, f"ドキュメントの更新に失敗しました。") from e
    finally:
        session.close()


def delete_document(_id: DocumentId) -> None:
    session = Session()
    try:
        entity = session.query(DocumentEntity).filter_by(id=_id).first()
        if not entity:
            raise AppError(ErrorKind.NOT_FOUND, f"ドキュメントが見つかりません: {_id}")
        session.delete(entity)
        session.commit()
    except Exception as e:
        session.rollback()
        raise AppError(ErrorKind.INTERNAL, f"ドキュメントの削除に失敗しました。") from e
    finally:
        session.close()
