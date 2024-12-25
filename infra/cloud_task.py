import json
from typing import Any

from google.cloud import tasks_v2

from config.envs import PROJECT_ID, TASK_QUEUE_TOKEN, CLOUD_RUN_SA, API_BASE_URL


def send_queue(name: str, path: str, payload: dict[str, Any]) -> None:
    client = tasks_v2.CloudTasksClient()
    parent = client.queue_path(PROJECT_ID, "asia-northeast1", name)
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
    client.create_task(request={"parent": parent, "task": task})
