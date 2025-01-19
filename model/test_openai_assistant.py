from datetime import datetime, timezone, timedelta

from model.document import DocumentId
from model.openai_assistant import OpenaiAssistant, OpenaiAssistantId, OpenaiThreadId


def test_openai_assistant_initialization() -> None:
    now = datetime.now(timezone.utc)
    assistant = OpenaiAssistant(
        _id=OpenaiAssistantId("123"),
        document_id=DocumentId("456"),
        thread_id=OpenaiThreadId("789"),
        used_at=now,
        created_at=now,
        updated_at=now,
    )

    assert assistant.id == "123"
    assert assistant.document_id == "456"
    assert assistant.thread_id == "789"
    assert assistant.used_at == now
    assert assistant.created_at == now
    assert assistant.updated_at == now


def test_openai_assistant_new() -> None:
    now = datetime.now(timezone.utc)
    assistant = OpenaiAssistant.new(
        _id=OpenaiAssistantId("123"),
        document_id=DocumentId("456"),
        thread_id=OpenaiThreadId("789"),
        now=now,
    )

    assert assistant.id == "123"
    assert assistant.document_id == "456"
    assert assistant.thread_id == "789"
    assert assistant.used_at == now
    assert assistant.created_at == now
    assert assistant.updated_at == now


def test_openai_assistant_use() -> None:
    now = datetime.now(timezone.utc)
    assistant = OpenaiAssistant(
        _id=OpenaiAssistantId("123"),
        document_id=DocumentId("456"),
        thread_id=OpenaiThreadId("789"),
        used_at=now,
        created_at=now,
        updated_at=now,
    )

    assert assistant.used_at == now

    updated_time = now + timedelta(days=1)
    assistant.use(updated_time)

    assert assistant.used_at == updated_time
    assert assistant.updated_at == updated_time
