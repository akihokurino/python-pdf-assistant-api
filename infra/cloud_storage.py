import os
from datetime import timedelta
from typing import Final

from google.cloud.storage import Client, Bucket, Blob
from google.oauth2.service_account import Credentials

_key_path: Final[str] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "../signer-cred.json"
)
_credentials: Final[Credentials] = Credentials.from_service_account_file(  # type: ignore
    _key_path,
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
_project_id: Final[str] = os.getenv("PROJECT_ID", "")
_bucket_name: Final[str] = f"{_project_id}-userdata"


def download(
    blob_name: str,
    destination_file_name: str,
    bucket_name: str = _bucket_name,
) -> None:
    client: Final[Client] = Client()
    bucket: Final[Bucket] = client.bucket(bucket_name)
    blob: Final[Blob] = bucket.blob(blob_name)
    blob.download_to_filename(destination_file_name)


def generate_pre_signed_upload_url(
    blob_name: str, bucket_name: str = _bucket_name, expiration_minutes: int = 15
) -> str:
    client: Final[Client] = Client()
    bucket: Final[Bucket] = client.bucket(bucket_name)
    blob: Final[Blob] = bucket.blob(blob_name)

    url: Final[str] = blob.generate_signed_url(
        credentials=_credentials,
        version="v4",
        expiration=timedelta(minutes=expiration_minutes),
        method="PUT",
        content_type="application/pdf",
    )
    return url
