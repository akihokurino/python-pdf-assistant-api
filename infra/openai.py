import time
from typing import Final, Tuple

from openai import OpenAI
from openai.pagination import SyncCursorPage
from openai.types.beta.assistant import Assistant
from openai.types.beta.thread import Thread
from openai.types.beta.threads import MessageContent, TextContentBlock, Run, Message

from config.envs import OPENAI_API_KEY
from model.document import (
    OpenaiAssistantId,
    OpenaiThreadId,
    DocumentId,
    OpenaiAssistant,
)
from model.error import AppError, ErrorKind

client: Final[OpenAI] = OpenAI(
    api_key=OPENAI_API_KEY,
)


def _wait_on_run(run: Run, thread: Thread) -> Run:
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run


def get_answer(_assistant: OpenaiAssistant, question: str) -> str:
    assistant: Final[Assistant] = client.beta.assistants.retrieve(
        assistant_id=_assistant.id
    )
    thread: Final[Thread] = client.beta.threads.retrieve(thread_id=_assistant.thread_id)

    new_message: Final[Message] = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=question,
    )
    run: Final[Run] = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )
    _wait_on_run(run, thread)
    response: SyncCursorPage[Message] = client.beta.threads.messages.list(
        thread_id=thread.id, order="asc", after=new_message.id
    )

    if response.data and response.data[0].content and len(response.data[0].content) > 0:
        content: MessageContent = response.data[0].content[0]
        if isinstance(content, TextContentBlock):
            return content.text.value
        else:
            raise AppError(ErrorKind.INTERNAL)
    else:
        raise AppError(ErrorKind.INTERNAL)


def create_assistant(
    document_id: DocumentId, document_path: str
) -> Tuple[OpenaiAssistantId, OpenaiThreadId]:
    assistant = client.beta.assistants.create(
        name=document_id,
        description=f"顧客向けアシスタント",
        model="gpt-4o-2024-11-20",
        instructions="""\
    あなたはアップロードされているPDFから特定の情報を抽出するための専用のアシスタントです。
    PDFの情報を参考にしながらユーザーの質問に回答してください
""",
        tools=[
            {"type": "code_interpreter"},
            {"type": "file_search"},
        ],
    )

    vector_store = client.beta.vector_stores.create(name="PDF Statements")
    file_streams = [open(document_path, "rb")]
    client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )
    assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )

    thread: Final[Thread] = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": "PDFの情報を元にこれからの質問に回答してください",
            }
        ]
    )

    return OpenaiAssistantId(assistant.id), OpenaiThreadId(thread.id)
