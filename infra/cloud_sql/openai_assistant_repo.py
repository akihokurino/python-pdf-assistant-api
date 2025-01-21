from datetime import datetime
from typing import Optional, List, Tuple, Any

from sqlalchemy.orm import joinedload
from sqlalchemy.orm import sessionmaker, Session as OrmSession

from adapter.adapter import OpenAIAssistantRepository
from infra.cloud_sql.entity import (
    openai_assistant_entity_from,
    openai_assistant_from,
    OpenaiAssistantEntity,
    document_from,
)
from model.document import DocumentId, Document
from model.error import AppError, ErrorKind
from model.openai_assistant import OpenaiAssistant


class OpenAIAssistantRepoImpl(OpenAIAssistantRepository):
    def __init__(
            self,
            session: Any,
    ) -> None:
        self.session = session

    @classmethod
    def new(
            cls,
            session: sessionmaker[OrmSession],
    ) -> OpenAIAssistantRepository:
        return cls(session)

    def find_past_openai_assistants(
            self,
            date: datetime,
    ) -> List[Tuple[OpenaiAssistant, Document]]:
        session = self.session()
        try:
            entities = (
                session.query(OpenaiAssistantEntity)
                .filter(OpenaiAssistantEntity.used_at < date)
                .options(joinedload(OpenaiAssistantEntity.document))
                .all()
            )
            return [(openai_assistant_from(e), document_from(e.document)) for e in entities]
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, f"データの取得に失敗しました。") from e
        finally:
            session.close()

    def get_assistant(self, _id: DocumentId) -> Optional[OpenaiAssistant]:
        session = self.session()
        try:
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
        finally:
            session.close()

    def insert_assistant(self, item: OpenaiAssistant) -> None:
        session = self.session()
        try:
            entity = openai_assistant_entity_from(item)
            session.add(entity)
            session.commit()
        except Exception as e:
            session.rollback()
            raise AppError(ErrorKind.INTERNAL, f"アシスタントの登録に失敗しました。") from e
        finally:
            session.close()

    def update_assistant(self, item: OpenaiAssistant) -> None:
        session = self.session()
        try:
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
            session.rollback()
            raise AppError(ErrorKind.INTERNAL, f"アシスタントの更新に失敗しました。") from e
        finally:
            session.close()

    def delete_assistant(self, _id: DocumentId) -> None:
        session = self.session()
        try:
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
            session.rollback()
            raise AppError(ErrorKind.INTERNAL, f"アシスタントの削除に失敗しました。") from e
        finally:
            session.close()
