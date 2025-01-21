from google.cloud.storage import Client

from infra.cloud_storage import CloudStorageAdapter

storage_adapter = CloudStorageAdapter.new(Client())
