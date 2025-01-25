import asyncio
from datetime import datetime, timezone, timedelta
from typing import Final

from adapter.adapter import OpenAIAdapter, AssistantRepository
from di.di import container
from model.document import Status


async def main() -> None:
    openai_adapter: OpenAIAdapter = container.openai_adapter()
    assistant_repository: AssistantRepository = container.assistant_repository()

    now: Final[datetime] = datetime.now(timezone.utc)
    target: Final[datetime] = now - timedelta(hours=3)

    results = await assistant_repository.find_past(target)
    for result in results:
        assistant = result[0]
        document = result[1]

        document.update_status(Status.PREPARE_ASSISTANT, now)
        openai_adapter.delete(assistant.id)
        await assistant_repository.delete_with_update_document(document.id, document)


if __name__ == "__main__":
    asyncio.run(main())
