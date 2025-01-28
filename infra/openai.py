import asyncio
import time
from typing import Final, final

from openai import OpenAI
from openai.pagination import SyncCursorPage
from openai.types.beta.assistant import Assistant
from openai.types.beta.thread import Thread
from openai.types.beta.threads import MessageContent, TextContentBlock, Run, Message
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from openai.types.chat.chat_completion_system_message_param import (
    ChatCompletionSystemMessageParam,
)
from openai.types.chat.chat_completion_user_message_param import (
    ChatCompletionUserMessageParam,
)

from adapter.adapter import OpenAIAdapter, ChatMessage
from domain.assistant import Assistant as AppAssistant, AssistantId, ThreadId
from domain.document import (
    DocumentId,
)
from domain.error import AppError, ErrorKind

MODEL: Final = "gpt-4o-2024-11-20"


@final
class OpenAIImpl:
    def __init__(
        self,
        cli: OpenAI,
    ) -> None:
        self.cli: Final = cli

    def __wait_on_run(self, run: Run, thread: Thread) -> Run:
        while run.status == "queued" or run.status == "in_progress":
            run = self.cli.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id,
            )
            time.sleep(0.5)
        return run

    def chat_assistant(self, _assistant: AppAssistant, message: str) -> str:
        assistant: Final[Assistant] = self.cli.beta.assistants.retrieve(
            assistant_id=_assistant.id
        )
        thread: Final[Thread] = self.cli.beta.threads.retrieve(
            thread_id=_assistant.thread_id
        )

        new_message: Final[Message] = self.cli.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=message,
        )
        run: Final[Run] = self.cli.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )
        self.__wait_on_run(run, thread)
        response: SyncCursorPage[Message] = self.cli.beta.threads.messages.list(
            thread_id=thread.id, order="asc", after=new_message.id
        )

        if (
            response.data
            and response.data[0].content
            and len(response.data[0].content) > 0
        ):
            content: MessageContent = response.data[0].content[0]
            if isinstance(content, TextContentBlock):
                return content.text.value
            else:
                raise AppError(ErrorKind.INTERNAL)
        else:
            raise AppError(ErrorKind.INTERNAL)

    def create_assistant(
        self, document_id: DocumentId, document_path: str
    ) -> tuple[AssistantId, ThreadId]:
        assistant = self.cli.beta.assistants.create(
            name=document_id,
            description=f"顧客向けアシスタント",
            model=MODEL,
            instructions="""\
        あなたはアップロードされているPDFから特定の情報を抽出するための専用のアシスタントです。
        PDFの情報を参考にしながらユーザーの質問に回答してください
    """,
            tools=[
                {"type": "code_interpreter"},
                {"type": "file_search"},
            ],
        )

        vector_store = self.cli.beta.vector_stores.create(name="PDF Statements")
        file_streams = [open(document_path, "rb")]
        self.cli.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id, files=file_streams
        )
        assistant = self.cli.beta.assistants.update(
            assistant_id=assistant.id,
            tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
        )

        thread: Final[Thread] = self.cli.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": "PDFの情報を元にこれからの質問に回答してください",
                }
            ]
        )

        return AssistantId(assistant.id), ThreadId(thread.id)

    def delete_assistant(self, assistant_id: AssistantId) -> None:
        self.cli.beta.assistants.delete(assistant_id=assistant_id)

    def chat_completion(self, messages: list[ChatMessage]) -> str:
        params: list[ChatCompletionMessageParam] = []
        for message in messages:
            if message.role == "system":
                params.append(
                    ChatCompletionSystemMessageParam(
                        role="system",
                        content=message.content,
                    )
                )
            if message.role == "user":
                params.append(
                    ChatCompletionUserMessageParam(
                        role="user",
                        content=message.content,
                    )
                )

        try:
            response = self.cli.chat.completions.create(
                model=MODEL,
                messages=params,
                max_tokens=1000,
                n=1,
                stop=None,
                temperature=0.7,
                top_p=1,
            )
            text = response.choices[0].message.content
            if text is None:
                raise AppError(ErrorKind.INTERNAL, "OpenAIでエラーが発生しました")
            return text
        except Exception as e:
            raise AppError(ErrorKind.INTERNAL, f"OpenAIでエラーが発生しました") from e


@final
class AsyncOpenAIImpl:
    def __init__(
        self,
        inner: OpenAIImpl,
    ) -> None:
        self.inner: Final = inner

    @classmethod
    def new(
        cls,
        inner: OpenAIImpl,
    ) -> OpenAIAdapter:
        return cls(inner=inner)

    async def chat_assistant(self, _assistant: AppAssistant, message: str) -> str:
        res = await asyncio.to_thread(
            self.inner.chat_assistant, _assistant=_assistant, message=message
        )
        return res

    async def create_assistant(
        self, document_id: DocumentId, document_path: str
    ) -> tuple[AssistantId, ThreadId]:
        res = await asyncio.to_thread(
            self.inner.create_assistant,
            document_id=document_id,
            document_path=document_path,
        )
        return res

    async def delete_assistant(self, assistant_id: AssistantId) -> None:
        await asyncio.to_thread(self.inner.delete_assistant, assistant_id=assistant_id)

    async def chat_completion(self, messages: list[ChatMessage]) -> str:
        res = await asyncio.to_thread(self.inner.chat_completion, messages=messages)
        return res
