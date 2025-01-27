from __future__ import annotations

from datetime import datetime
from typing import TypedDict, Final

from google.cloud.firestore import DocumentSnapshot

from domain.assistant import (
    AssistantId,
    Assistant,
    ThreadId,
    MessageRole,
    Message,
    MessageId,
)

ASSISTANT_KIND: Final = "Assistant"
MESSAGE_KIND: Final = "Message"


class AssistantEntity(TypedDict):
    id: AssistantId
    created_at: str


def assistant_entity_from(d: Assistant) -> AssistantEntity:
    return AssistantEntity(
        id=d.id,
        created_at=d.created_at.isoformat(),
    )


class MessageEntity(TypedDict):
    id: MessageId
    thread_id: ThreadId
    role: MessageRole
    message: str
    created_at: str


def message_entity_from(d: Message) -> MessageEntity:
    return MessageEntity(
        id=d.id,
        thread_id=d.thread_id,
        role=d.role,
        message=d.message,
        created_at=d.created_at.isoformat(),
    )


def message_from(doc: DocumentSnapshot) -> Message:
    return Message(
        id=MessageId(doc.id),
        thread_id=ThreadId(doc.get("thread_id")),
        role=doc.get("role"),
        message=doc.get("message"),
        created_at=datetime.fromisoformat(doc.get("created_at")),
    )
