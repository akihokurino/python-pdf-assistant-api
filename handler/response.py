from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel

from model.document import Document, Status
from model.user import User


class MeResp(BaseModel):
    user: UserResp
    documents: List[DocumentResp]

    @classmethod
    def from_model(cls, user: User, document: List[Document]) -> MeResp:
        return cls(
            user=UserResp.from_model(user),
            documents=[DocumentResp.from_model(doc) for doc in document],
        )


class UserResp(BaseModel):
    id: str
    name: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, user: User) -> UserResp:
        return cls(
            id=user.id,
            name=user.name,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class DocumentResp(BaseModel):
    id: str
    user_id: str
    name: str
    description: str
    gs_file_url: str
    status: Status
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, document: Document) -> DocumentResp:
        return cls(
            id=document.id,
            user_id=document.user_id,
            name=document.name,
            description=document.description,
            gs_file_url=document.gs_file_url,
            status=document.status,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )


class DocumentWithUserResp(BaseModel):
    user: UserResp
    document: DocumentResp

    @classmethod
    def from_model(cls, user: User, document: Document) -> DocumentWithUserResp:
        return cls(
            user=UserResp.from_model(user),
            document=DocumentResp.from_model(document),
        )


class PreSignUploadResp(BaseModel):
    url: str
    key: str


class PreSignGetResp(BaseModel):
    url: str


class AnswerResp(BaseModel):
    answer: str


class EmptyResp(BaseModel):
    pass
