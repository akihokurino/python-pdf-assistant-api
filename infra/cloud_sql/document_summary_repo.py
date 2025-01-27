from typing import final, Final

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.future import select

from adapter.adapter import DocumentSummaryRepository
from domain.document import DocumentId, DocumentSummary
from domain.error import ErrorKind, AppError
from infra.cloud_sql.entity import (
    document_summary_entity_from,
    DocumentSummaryEntity,
    document_summary_from,
)


@final
class DocumentSummaryRepoImpl:
    def __init__(
            self,
            session: async_sessionmaker[AsyncSession],
    ) -> None:
        self.session: Final = session

    @classmethod
    def new(
            cls,
            session: async_sessionmaker[AsyncSession],
    ) -> DocumentSummaryRepository:
        return cls(session)

    async def find_by_document(self, document_id: DocumentId) -> list[DocumentSummary]:
        try:
            async with self.session() as session:
                entities = (
                    (
                        await session.execute(
                            select(DocumentSummaryEntity).filter_by(
                                document_id=document_id
                            )
                        )
                    )
                    .scalars()
                    .all()
                )
                return [document_summary_from(e) for e in entities]
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL) from e

    async def insert(self, summary: DocumentSummary) -> None:
        try:
            async with self.session() as session:
                entity = document_summary_entity_from(summary)
                session.add(entity)
                await session.commit()
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL) from e

    async def delete_by_document(self, document_id: DocumentId) -> None:
        try:
            async with self.session() as session:
                stmt = delete(DocumentSummaryEntity).where(
                    DocumentSummaryEntity.document_id == document_id
                )
                await session.execute(stmt)
                await session.commit()
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL) from e
