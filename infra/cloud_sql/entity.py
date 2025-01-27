from __future__ import annotations

from datetime import datetime
from typing import final

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped

from model.assistant import Assistant, ThreadId, AssistantId
from model.document import (
    Document,
    DocumentId,
    Status,
    DocumentSummary,
    DocumentSummaryId,
)
from model.user import User, UserId

Base = declarative_base()


@final
class UserEntity(Base):
    __tablename__ = "users"

    id: str = Column(String(255), primary_key=True)
    name: str = Column(String(255), nullable=False)
    created_at: datetime = Column(DateTime(timezone=True), nullable=False)
    updated_at: datetime = Column(DateTime(timezone=True), nullable=False)

    documents: Mapped[list["DocumentEntity"]] = relationship(
        "DocumentEntity", back_populates="user"
    )

    def update(self, user: User) -> None:
        self.name = user.name
        self.updated_at = user.updated_at


def user_entity_from(d: User) -> UserEntity:
    return UserEntity(
        id=d.id,
        name=d.name,
        created_at=d.created_at,
        updated_at=d.updated_at,
    )


def user_from(e: UserEntity) -> User:
    return User(
        id=UserId(e.id),
        name=e.name,
        created_at=e.created_at,
        updated_at=e.updated_at,
    )


@final
class DocumentEntity(Base):
    __tablename__ = "documents"

    id: str = Column(String(255), primary_key=True)
    user_id: str = Column(String(255), ForeignKey("users.id"), nullable=False)
    name: str = Column(String(255), nullable=False)
    description: str = Column(String(255), nullable=False)
    gs_file_url: str = Column(String(255), nullable=False)
    status: int = Column(Integer(), nullable=False)
    created_at: datetime = Column(DateTime(timezone=True), nullable=False)
    updated_at: datetime = Column(DateTime(timezone=True), nullable=False)

    user: Mapped["UserEntity"] = relationship("UserEntity", back_populates="documents")
    assistant: Mapped["AssistantEntity"] = relationship(
        "AssistantEntity", back_populates="document"
    )
    summaries: Mapped[list["DocumentSummaryEntity"]] = relationship(
        "DocumentSummaryEntity", back_populates="document"
    )

    def update(self, document: Document) -> None:
        self.name = document.name
        self.description = document.description
        self.gs_file_url = document.gs_file_url
        self.status = document.status.value
        self.updated_at = document.updated_at


def document_entity_from(d: Document) -> DocumentEntity:
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


def document_from(e: DocumentEntity) -> Document:
    return Document(
        id=DocumentId(e.id),
        user_id=UserId(e.user_id),
        name=e.name,
        description=e.description,
        gs_file_url=e.gs_file_url,
        status=Status(e.status),
        created_at=e.created_at,
        updated_at=e.updated_at,
    )


@final
class DocumentSummaryEntity(Base):
    __tablename__ = "document_summaries"

    id: str = Column(String(255), primary_key=True)
    document_id: str = Column(String(255), ForeignKey("documents.id"), nullable=False)
    text: str = Column(Text, nullable=False)
    index: int = Column(Integer(), nullable=False)
    created_at: datetime = Column(DateTime(timezone=True), nullable=False)
    updated_at: datetime = Column(DateTime(timezone=True), nullable=False)

    document: Mapped["DocumentEntity"] = relationship(
        "DocumentEntity", back_populates="summaries"
    )


def document_summary_entity_from(d: DocumentSummary) -> DocumentSummaryEntity:
    return DocumentSummaryEntity(
        id=d.id,
        document_id=d.document_id,
        text=d.text,
        index=d.index,
        created_at=d.created_at,
        updated_at=d.updated_at,
    )


def document_summary_from(e: DocumentSummaryEntity) -> DocumentSummary:
    return DocumentSummary(
        id=DocumentSummaryId(e.id),
        document_id=DocumentId(e.document_id),
        text=e.text,
        index=e.index,
        created_at=e.created_at,
        updated_at=e.updated_at,
    )


@final
class AssistantEntity(Base):
    __tablename__ = "assistants"

    document_id: str = Column(String(255), ForeignKey("documents.id"), primary_key=True)
    assistant_id: str = Column(String(255), nullable=False)
    thread_id: str = Column(String(255), nullable=False)
    used_at: datetime = Column(DateTime(timezone=True), nullable=False)
    created_at: datetime = Column(DateTime(timezone=True), nullable=False)
    updated_at: datetime = Column(DateTime(timezone=True), nullable=False)

    document: Mapped["DocumentEntity"] = relationship(
        "DocumentEntity", back_populates="assistant"
    )

    def update(self, assistant: Assistant) -> None:
        self.used_at = assistant.used_at
        self.updated_at = assistant.updated_at


def assistant_entity_from(d: Assistant) -> AssistantEntity:
    return AssistantEntity(
        document_id=d.document_id,
        assistant_id=d.id,
        thread_id=d.thread_id,
        used_at=d.used_at,
        created_at=d.created_at,
        updated_at=d.updated_at,
    )


def assistant_from(e: AssistantEntity) -> Assistant:
    return Assistant(
        id=AssistantId(e.assistant_id),
        document_id=DocumentId(e.document_id),
        thread_id=ThreadId(e.thread_id),
        used_at=e.used_at,
        created_at=e.created_at,
        updated_at=e.updated_at,
    )
