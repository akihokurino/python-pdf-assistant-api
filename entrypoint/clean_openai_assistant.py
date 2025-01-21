from datetime import datetime, timezone, timedelta
from typing import Final

from di.di import openai_adapter, openai_assistant_repository
from model.document import Status

if __name__ == "__main__":
    now: Final[datetime] = datetime.now(timezone.utc)
    target: Final[datetime] = now - timedelta(hours=3)

    results = openai_assistant_repository.find_past_openai_assistants(target)
    for result in results:
        assistant = result[0]
        document = result[1]

        document.update_status(Status.PREPARE_ASSISTANT, now)
        openai_adapter.delete_assistant(assistant.id)
        openai_assistant_repository.delete_assistant_and_update_document(document.id, document)
