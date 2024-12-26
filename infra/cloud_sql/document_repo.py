from typing import Optional, List, Tuple

from sqlalchemy.orm import joinedload

from infra.cloud_sql.common import Session
from infra.cloud_sql.entity import (
    DocumentEntity,
    document_from,
    document_entity_from,
    user_from,
)
from model.document import Document, DocumentId
from model.error import ErrorKind, AppError
from model.user import UserId, User


def find_documents_by_user(user_id: UserId) -> List[Document]:
    session = Session()
    try:
        entities = session.query(DocumentEntity).filter_by(user_id=user_id).all()
        return [document_from(e) for e in entities]
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
        return document_from(entity)
    except Exception as e:
        raise AppError(ErrorKind.INTERNAL, f"ドキュメントの取得に失敗しました。") from e
    finally:
        session.close()


def get_document_with_user(_id: DocumentId) -> Optional[Tuple[Document, User]]:
    session = Session()
    try:
        entity = (
            session.query(DocumentEntity)
            .filter_by(id=_id)
            .options(joinedload(DocumentEntity.user))
            .one_or_none()
        )
        if not entity:
            return None
        return document_from(entity), user_from(entity.user)
    except Exception as e:

        raise AppError(ErrorKind.INTERNAL, f"ドキュメントの取得に失敗しました。") from e
    finally:
        session.close()


def insert_document(item: Document) -> None:
    session = Session()
    try:
        entity = document_entity_from(item)
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
        entity = session.query(DocumentEntity).filter_by(id=item.id).one_or_none()
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
        entity = session.query(DocumentEntity).filter_by(id=_id).one_or_none()
        if not entity:
            raise AppError(ErrorKind.NOT_FOUND, f"ドキュメントが見つかりません: {_id}")
        session.delete(entity)
        session.commit()
    except Exception as e:
        session.rollback()
        raise AppError(ErrorKind.INTERNAL, f"ドキュメントの削除に失敗しました。") from e
    finally:
        session.close()
