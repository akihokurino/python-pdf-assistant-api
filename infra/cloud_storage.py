import os
from datetime import timedelta
from typing import Final, final

import google.auth
from google.auth.transport import requests
from google.cloud.storage import Client, Bucket, Blob
from google.oauth2.service_account import Credentials

from adapter.adapter import StorageAdapter
from config.envs import DEFAULT_BUCKET_NAME
from model.error import AppError, ErrorKind


def _local_credentials() -> Credentials:
    key_path: Final[str] = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "../signer-cred.json"
    )
    credentials: Final[Credentials] = Credentials.from_service_account_file(  # type: ignore
        key_path,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    return credentials


def _credential() -> Credentials:
    # https://stackoverflow.com/questions/64234214/how-to-generate-a-blob-signed-url-in-google-cloud-run
    credentials, _ = google.auth.default()  # type: ignore
    credentials.refresh(requests.Request())  # type: ignore
    cred: Final[Credentials] = credentials
    return cred


@final
class CloudStorageImpl(StorageAdapter):
    def __init__(
            self,
            cli: Client,
    ) -> None:
        self.cli: Final = cli

    @classmethod
    def new(
            cls,
            cli: Client,
    ) -> StorageAdapter:
        return cls(cli)

    def download_object(
            self,
            key: str,
            destination_file_name: str,
            bucket_name: str = DEFAULT_BUCKET_NAME,
    ) -> None:
        bucket: Final[Bucket] = self.cli.bucket(bucket_name)
        blob: Final[Blob] = bucket.blob(key)
        blob.download_to_filename(destination_file_name)

    def gen_pre_signed_upload_url(
            self,
            key: str,
            bucket_name: str = DEFAULT_BUCKET_NAME,
            expiration_minutes: int = 15,
    ) -> str:
        bucket: Final[Bucket] = self.cli.bucket(bucket_name)
        blob: Final[Blob] = bucket.blob(key)

        if os.getenv("IS_LOCAL", "") == "true":
            url: str = blob.generate_signed_url(
                credentials=_local_credentials(),
                version="v4",
                expiration=timedelta(minutes=expiration_minutes),
                method="PUT",
                content_type="application/pdf",
            )
        else:
            credentials = _credential()
            url = blob.generate_signed_url(
                access_token=credentials.token,
                service_account_email=credentials.service_account_email,
                version="v4",
                expiration=timedelta(minutes=expiration_minutes),
                method="PUT",
                content_type="application/pdf",
            )

        return url

    def gen_pre_signed_get_url(
            self,
            key: str,
            bucket_name: str = DEFAULT_BUCKET_NAME,
            expiration_minutes: int = 15,
    ) -> str:
        bucket: Final[Bucket] = self.cli.bucket(bucket_name)
        blob: Final[Blob] = bucket.blob(key)
        if os.getenv("IS_LOCAL", "") == "true":
            url: str = blob.generate_signed_url(
                credentials=_local_credentials(),
                version="v4",
                expiration=timedelta(minutes=expiration_minutes),
                method="GET",
            )
        else:
            credentials = _credential()
            url = blob.generate_signed_url(
                access_token=credentials.token,
                service_account_email=credentials.service_account_email,
                version="v4",
                expiration=timedelta(minutes=expiration_minutes),
                method="GET",
            )

        return url

    def delete_object(self, key: str, bucket_name: str = DEFAULT_BUCKET_NAME) -> None:
        bucket: Final[Bucket] = self.cli.bucket(bucket_name)
        blob: Final[Blob] = bucket.blob(key)

        if blob.exists():
            blob.delete()
        else:
            raise AppError(ErrorKind.NOT_FOUND, f"指定されたキーが存在しません: {key}")
