from typing import Final

from google.cloud.secretmanager import SecretManagerServiceClient
from google.cloud.secretmanager_v1.types.service import AccessSecretVersionResponse


def get_secret(project_id: str, secret_id: str, version_id: str) -> str:
    client: Final[SecretManagerServiceClient] = SecretManagerServiceClient()
    name: Final[str] = client.secret_version_path(project_id, secret_id, version_id)
    response: Final[AccessSecretVersionResponse] = client.access_secret_version(
        name=name
    )
    return response.payload.data.decode("UTF-8")
