from datetime import datetime, timezone, timedelta

from model.document import Document, DocumentId, Status
from model.user import UserId


def test_document_initialization() -> None:
    now = datetime.now(timezone.utc)
    document = Document(
        _id=DocumentId("123"),
        user_id=UserId("456"),
        name="SamplePDF",
        description="This is a sample PDF",
        gs_file_url="gs://bucket/sample.pdf",
        status=Status.PREPARE_ASSISTANT,
        created_at=now,
        updated_at=now,
    )

    assert document.id == "123"
    assert document.user_id == "456"
    assert document.name == "SamplePDF"
    assert document.description == "This is a sample PDF"
    assert document.gs_file_url == "gs://bucket/sample.pdf"
    assert document.status == Status.PREPARE_ASSISTANT
    assert document.created_at == now
    assert document.updated_at == now


def test_document_new() -> None:
    now = datetime.now(timezone.utc)
    document = Document.new(
        user_id=UserId("456"),
        name="SamplePDF",
        description="This is a sample PDF",
        gs_file_url="gs://bucket/sample.pdf",
        now=now,
    )

    assert document.user_id == "456"
    assert document.name == "SamplePDF"
    assert document.description == "This is a sample PDF"
    assert document.gs_file_url == "gs://bucket/sample.pdf"
    assert document.status == Status.PREPARE_ASSISTANT
    assert document.created_at == now
    assert document.updated_at == now


def test_document_update() -> None:
    now = datetime.now(timezone.utc)
    document = Document(
        _id=DocumentId("123"),
        user_id=UserId("456"),
        name="SamplePDF",
        description="This is a sample PDF",
        gs_file_url="gs://bucket/sample.pdf",
        status=Status.PREPARE_ASSISTANT,
        created_at=now,
        updated_at=now,
    )

    assert document.name == "SamplePDF__"
    assert document.updated_at == now

    updated_time = now + timedelta(days=1)
    document.update(name="UpdatePDF", description="updated", now=updated_time)

    assert document.name == "UpdatePDF"
    assert document.description == "updated"
    assert document.created_at == now
    assert document.updated_at == updated_time


def test_document_update_status() -> None:
    now = datetime.now(timezone.utc)
    document = Document(
        _id=DocumentId("123"),
        user_id=UserId("456"),
        name="SamplePDF",
        description="This is a sample PDF",
        gs_file_url="gs://bucket/sample.pdf",
        status=Status.PREPARE_ASSISTANT,
        created_at=now,
        updated_at=now,
    )

    assert document.status is Status(Status.PREPARE_ASSISTANT)
    assert document.updated_at == now

    updated_time = now + timedelta(days=1)
    document.update_status(status=Status.READY_ASSISTANT, now=updated_time)

    assert document.status is Status(Status.READY_ASSISTANT)
    assert document.created_at == now
    assert document.updated_at == updated_time
