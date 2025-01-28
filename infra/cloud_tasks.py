import asyncio
import json
from typing import Any, Final, final

from google.cloud import tasks_v2

from adapter.adapter import TaskQueueAdapter
from config.envs import PROJECT_ID, TASK_QUEUE_TOKEN, CLOUD_RUN_SA, API_BASE_URL


@final
class CloudTasksImpl:
    def __init__(
        self,
        cli: tasks_v2.CloudTasksClient,
    ) -> None:
        self.cli: Final = cli

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


@final
class AsyncCloudTasksImpl:
    def __init__(
        self,
        inner: CloudTasksImpl,
    ) -> None:
        self.inner: Final = inner

    @classmethod
    def new(
        cls,
        inner: CloudTasksImpl,
    ) -> TaskQueueAdapter:
        return cls(inner=inner)

    async def send_queue(self, name: str, path: str, payload: dict[str, Any]) -> None:
        await asyncio.to_thread(
            self.inner.send_queue, name=name, path=path, payload=payload
        )
