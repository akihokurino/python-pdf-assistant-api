from datetime import datetime, timezone, timedelta
from typing import Final

from di.di import openai_adapter
from infra.cloud_sql.document_repo import update_document
from infra.cloud_sql.openai_assistant_repo import (
    find_past_openai_assistants,
    delete_assistant,
)
from model.document import Status

if __name__ == "__main__":
    now: Final[datetime] = datetime.now(timezone.utc)
    target: Final[datetime] = now - timedelta(hours=3)

    results = find_past_openai_assistants(target)
    for result in results:
        assistant = result[0]
        document = result[1]

        document.update_status(Status.PREPARE_ASSISTANT, now)
        openai_adapter.delete_assistant(assistant.id)
        update_document(document)
        delete_assistant(document.id)
