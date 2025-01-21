import json
from typing import Any, Final

from google.cloud import tasks_v2

from adapter.adapter import TaskQueueAdapter
from config.envs import PROJECT_ID, TASK_QUEUE_TOKEN, CLOUD_RUN_SA, API_BASE_URL


class CloudTasks(TaskQueueAdapter):
    def __init__(
        self,
        cli: tasks_v2.CloudTasksClient,
    ) -> None:
        self.cli: Final[tasks_v2.CloudTasksClient] = cli

    @classmethod
    def new(
        cls,
        cli: tasks_v2.CloudTasksClient,
    ) -> TaskQueueAdapter:
        return cls(cli)

    def send_queue(self, name: str, path: str, payload: dict[str, Any]) -> None:
        parent = self.cli.queue_path(PROJECT_ID, "asia-northeast1", name)
        url = f"{API_BASE_URL}{path}"
        payload_encoded = json.dumps(payload).encode("utf-8")
        task = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": url,
                "headers": {
                    "Content-Type": "application/json",
                    "x-queue-token": TASK_QUEUE_TOKEN,
                },
                "oidc_token": {"service_account_email": CLOUD_RUN_SA},
                "body": payload_encoded,
            }
        }
        self.cli.create_task(request={"parent": parent, "task": task})
