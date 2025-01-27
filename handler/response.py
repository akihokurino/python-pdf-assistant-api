from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from model.assistant import AssistantId, ThreadId, Assistant, MessageId, Message
from model.document import Document, Status, DocumentId
from model.user import User, UserId


class MeResp(BaseModel):
    user: UserResp
    documents: list[DocumentResp]

    @classmethod
    def from_model(cls, user: User, document: list[Document]) -> MeResp:
        return cls(
            user=UserResp.from_model(user),
            documents=[DocumentResp.from_model(doc) for doc in document],
        )


class UserResp(BaseModel):
    id: UserId
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
    id: DocumentId
    user_id: UserId
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


class DocumentWithUserAndAssistantResp(BaseModel):
    user: UserResp
    document: DocumentResp
    assistant: Optional[AssistantResp]

    @classmethod
    def from_model(
            cls, user: User, document: Document, assistant: Optional[Assistant]
    ) -> DocumentWithUserAndAssistantResp:
        return cls(
            user=UserResp.from_model(user),
            document=DocumentResp.from_model(document),
            assistant=AssistantResp.from_model(assistant) if assistant else None,
        )


class AssistantResp(BaseModel):
    id: AssistantId
    thread_id: ThreadId
    used_at: datetime
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, assistant: Assistant) -> AssistantResp:
        return cls(
            id=assistant.id,
            thread_id=assistant.thread_id,
            used_at=assistant.used_at,
            created_at=assistant.created_at,
            updated_at=assistant.updated_at,
        )


class MessageResp(BaseModel):
    id: MessageId
    thread_id: ThreadId
    role: str
    message: str
    created_at: datetime

    @classmethod
    def from_model(cls, message: Message) -> MessageResp:
        return cls(
            id=message.id,
            thread_id=message.thread_id,
            role=message.role,
            message=message.message,
            created_at=message.created_at,
        )


class PreSignUploadResp(BaseModel):
    url: str
    key: str


class PreSignGetResp(BaseModel):
    url: str


class EmptyResp(BaseModel):
    pass


class TextResp(BaseModel):
    text: str
