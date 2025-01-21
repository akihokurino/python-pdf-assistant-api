from datetime import datetime
from typing import Optional, List, Tuple, Any

from sqlalchemy.orm import joinedload
from sqlalchemy.orm import sessionmaker, Session as OrmSession

from adapter.adapter import OpenaiAssistantRepository
from infra.cloud_sql.entity import (
    openai_assistant_entity_from,
    openai_assistant_from,
    OpenaiAssistantEntity,
    document_from, DocumentEntity,
)
from model.document import DocumentId, Document
from model.error import AppError, ErrorKind
from model.openai_assistant import OpenaiAssistant


class OpenaiAssistantRepoImpl(OpenaiAssistantRepository):
    def __init__(
            self,
            session: Any,
    ) -> None:
        self.session = session

    @classmethod
    def new(
            cls,
            session: sessionmaker[OrmSession],
    ) -> OpenaiAssistantRepository:
        return cls(session)

    def find_past_openai_assistants(
            self,
            date: datetime,
    ) -> List[Tuple[OpenaiAssistant, Document]]:
        try:
            with self.session() as session:
                entities = (
                    session.query(OpenaiAssistantEntity)
                    .filter(OpenaiAssistantEntity.used_at < date)
                    .options(joinedload(OpenaiAssistantEntity.document))
                    .all()
                )
                return [(openai_assistant_from(e), document_from(e.document)) for e in entities]
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, f"データの取得に失敗しました。") from e

    def get_assistant(self, _id: DocumentId) -> Optional[OpenaiAssistant]:
        try:
            with self.session() as session:
                entity = (
                    session.query(OpenaiAssistantEntity)
                    .filter_by(document_id=_id)
                    .one_or_none()
                )
                if not entity:
                    return None
                return openai_assistant_from(entity)
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, f"アシスタントの取得に失敗しました。") from e

    def insert_assistant(self, item: OpenaiAssistant) -> None:
        try:
            with self.session() as session:
                entity = openai_assistant_entity_from(item)
                session.add(entity)
                session.commit()
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, f"アシスタントの登録に失敗しました。") from e

    def insert_assistant_and_update_document(self, assistant: OpenaiAssistant, document: Document) -> None:
        try:
            with self.session() as session:
                entity1 = openai_assistant_entity_from(assistant)
                session.add(entity1)

                entity2 = session.query(DocumentEntity).filter_by(id=assistant.id).one_or_none()
                if not entity2:
                    raise AppError(
                        ErrorKind.NOT_FOUND, f"ドキュメントが見つかりません: {assistant.id}"
                    )
                entity2.update(assistant)

                session.commit()
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, f"アシスタントの登録に失敗しました。") from e

    def update_assistant(self, item: OpenaiAssistant) -> None:
        try:
            with self.session() as session:
                entity = (
                    session.query(OpenaiAssistantEntity).filter_by(document_id=item.document_id)
                ).one_or_none()

                if not entity:
                    raise AppError(
                        ErrorKind.NOT_FOUND, f"アシスタントが見つかりません: {item.id}"
                    )
                entity.update(item)
                session.commit()
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, f"アシスタントの更新に失敗しました。") from e

    def delete_assistant(self, _id: DocumentId) -> None:
        try:
            with self.session() as session:
                entity = (
                    session.query(OpenaiAssistantEntity)
                    .filter_by(document_id=_id)
                    .one_or_none()
                )
                if not entity:
                    raise AppError(ErrorKind.NOT_FOUND, f"アシスタントが見つかりません: {_id}")
                session.delete(entity)
                session.commit()
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, f"アシスタントの削除に失敗しました。") from e

    def delete_assistant_and_update_document(self, _id: DocumentId, document: Document) -> None:
        try:
            with self.session() as session:
                entity1 = (
                    session.query(OpenaiAssistantEntity)
                    .filter_by(document_id=_id)
                    .one_or_none()
                )
                if not entity1:
                    raise AppError(ErrorKind.NOT_FOUND, f"アシスタントが見つかりません: {_id}")
                session.delete(entity1)

                entity2 = session.query(DocumentEntity).filter_by(id=document.id).one_or_none()
                if not entity2:
                    raise AppError(
                        ErrorKind.NOT_FOUND, f"ドキュメントが見つかりません: {document.id}"
                    )
                entity2.update(document)

                session.commit()
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, f"アシスタントの削除に失敗しました。") from e
