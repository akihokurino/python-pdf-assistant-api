from google.cloud import tasks_v2
from google.cloud.storage import Client

from infra.cloud_storage import CloudStorage
from infra.cloud_tasks import CloudTasks

storage_adapter = CloudStorage.new(Client())
task_queue_adapter = CloudTasks.new(tasks_v2.CloudTasksClient())
