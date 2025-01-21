from typing import Optional, List, Tuple, Any

from sqlalchemy.orm import joinedload
from sqlalchemy.orm import sessionmaker, Session as OrmSession

from adapter.adapter import DocumentRepository
from infra.cloud_sql.entity import (
    DocumentEntity,
    document_from,
    document_entity_from,
    user_from,
)
from model.document import Document, DocumentId
from model.error import ErrorKind, AppError
from model.user import UserId, User


class DocumentRepoImpl(DocumentRepository):
    def __init__(
            self,
            session: Any,
    ) -> None:
        self.session = session

    @classmethod
    def new(
            cls,
            session: sessionmaker[OrmSession],
    ) -> DocumentRepository:
        return cls(session)

    def find_documents_by_user(self, user_id: UserId) -> List[Document]:
        try:
            with self.session() as session:
                entities = session.query(DocumentEntity).filter_by(user_id=user_id).all()
                return [document_from(e) for e in entities]
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, f"ドキュメントの取得に失敗しました。") from e

    def get_document(self, _id: DocumentId) -> Optional[Document]:
        try:
            with self.session() as session:
                entity = session.query(DocumentEntity).filter_by(id=_id).one_or_none()
                if not entity:
                    return None
                return document_from(entity)
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, f"ドキュメントの取得に失敗しました。") from e

    def get_document_with_user(self, _id: DocumentId) -> Optional[Tuple[Document, User]]:
        try:
            with self.session() as session:
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

    def insert_document(self, item: Document) -> None:
        try:
            with self.session() as session:
                entity = document_entity_from(item)
                session.add(entity)
                session.commit()
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, f"ドキュメントの登録に失敗しました。") from e

    def update_document(self, item: Document) -> None:
        try:
            with self.session() as session:
                entity = session.query(DocumentEntity).filter_by(id=item.id).one_or_none()
                if not entity:
                    raise AppError(
                        ErrorKind.NOT_FOUND, f"ドキュメントが見つかりません: {item.id}"
                    )
                entity.update(item)
                session.commit()
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, f"ドキュメントの更新に失敗しました。") from e

    def delete_document(self, _id: DocumentId) -> None:
        try:
            with self.session() as session:
                entity = session.query(DocumentEntity).filter_by(id=_id).one_or_none()
                if not entity:
                    raise AppError(ErrorKind.NOT_FOUND, f"ドキュメントが見つかりません: {_id}")
                session.delete(entity)
                session.commit()
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, f"ドキュメントの削除に失敗しました。") from e
