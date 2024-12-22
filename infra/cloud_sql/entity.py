from __future__ import annotations

from datetime import datetime
from typing import final, List

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from infra.cloud_sql.common import Base
from model.document import Document, DocumentId, Status
from model.user import User, UserId


@final
class UserEntity(Base):
    __tablename__ = "users"

    id: str = Column(String(255), primary_key=True)
    name: str = Column(String(255), nullable=False)
    created_at: datetime = Column(DateTime, nullable=False)
    updated_at: datetime = Column(DateTime, nullable=False)

    documents: Mapped[List["DocumentEntity"]] = relationship(
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
        _id=UserId(e.id),
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
    created_at: datetime = Column(DateTime, nullable=False)
    updated_at: datetime = Column(DateTime, nullable=False)

    user: Mapped["UserEntity"] = relationship("UserEntity", back_populates="documents")

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
        _id=DocumentId(e.id),
        user_id=UserId(e.user_id),
        name=e.name,
        description=e.description,
        gs_file_url=e.gs_file_url,
        status=Status(e.status),
        created_at=e.created_at,
        updated_at=e.updated_at,
    )
