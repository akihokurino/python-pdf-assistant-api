from typing import Final

from google.cloud import tasks_v2
from google.cloud.storage import Client
from openai import OpenAI

from adapter.adapter import StorageAdapter, TaskQueueAdapter, LogAdapter, OpenAIAdapter
from config.envs import OPENAI_API_KEY
from infra.cloud_storage import CloudStorageImpl
from infra.cloud_tasks import CloudTasksImpl
from infra.logger import LoggerImpl
from infra.openai import OpenAIImpl

storage_adapter: Final[StorageAdapter] = CloudStorageImpl.new(Client())
task_queue_adapter: Final[TaskQueueAdapter] = CloudTasksImpl.new(
    tasks_v2.CloudTasksClient()
)
log_adapter: Final[LogAdapter] = LoggerImpl.new()
openai_adapter: Final[OpenAIAdapter] = OpenAIImpl.new(
    OpenAI(
        api_key=OPENAI_API_KEY,
    )
)
