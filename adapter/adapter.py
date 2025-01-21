from typing import Protocol

from config.envs import DEFAULT_BUCKET_NAME


class StorageAdapter(Protocol):
    def download_object(
            self,
            key: str,
            destination_file_name: str,
            bucket_name: str = DEFAULT_BUCKET_NAME,
    ) -> None: ...

    def gen_pre_signed_upload_url(
            self,
            key: str,
            bucket_name: str = DEFAULT_BUCKET_NAME,
            expiration_minutes: int = 15,
    ) -> str: ...

    def gen_pre_signed_get_url(
            self,
            key: str,
            bucket_name: str = DEFAULT_BUCKET_NAME,
            expiration_minutes: int = 15,
    ) -> str: ...

    def delete_object(
            self, key: str, bucket_name: str = DEFAULT_BUCKET_NAME
    ) -> None: ...
