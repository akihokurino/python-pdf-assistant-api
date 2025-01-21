from typing import Final

from google.cloud import tasks_v2
from google.cloud.storage import Client

from adapter.adapter import StorageAdapter, TaskQueueAdapter, LogAdapter
from infra.cloud_storage import CloudStorage
from infra.cloud_tasks import CloudTasks
from infra.logger import Logger

storage_adapter: Final[StorageAdapter] = CloudStorage.new(Client())
task_queue_adapter: Final[TaskQueueAdapter] = CloudTasks.new(
    tasks_v2.CloudTasksClient()
)
log_adapter: Final[LogAdapter] = Logger.new()
