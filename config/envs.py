from __future__ import annotations

import os
from typing import Final

from google.cloud.secretmanager import SecretManagerServiceClient
from google.cloud.secretmanager_v1.types.service import AccessSecretVersionResponse


def get_secret(pid: str, secret_id: str, version_id: str) -> str:
    client: Final[SecretManagerServiceClient] = SecretManagerServiceClient()
    name: Final[str] = client.secret_version_path(pid, secret_id, version_id)
    response: Final[AccessSecretVersionResponse] = client.access_secret_version(
        name=name
    )
    return response.payload.data.decode("UTF-8")


PROJECT_ID: Final[str] = os.getenv("PROJECT_ID", "")
if os.getenv("IS_LOCAL", "") == "true":
    DATABASE_URL = "postgresql+psycopg2://postgres:pass@localhost/main"
else:
    DATABASE_URL = get_secret(PROJECT_ID, "cloud-sql-connection", "latest")
TASK_QUEUE_TOKEN: Final[str] = get_secret(PROJECT_ID, "task-queue-token", "latest")
CLOUD_RUN_SA: Final[str] = f"cloud-run-sa@{PROJECT_ID}.iam.gserviceaccount.com"
DEFAULT_BUCKET_NAME: Final[str] = f"{PROJECT_ID}-userdata"
API_BASE_URL: Final[str] = get_secret(PROJECT_ID, "api-base-url", "latest")
OPENAI_API_KEY: Final[str] = get_secret(PROJECT_ID, "openai-api-key", "latest")
