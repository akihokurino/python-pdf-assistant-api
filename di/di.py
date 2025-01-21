from typing import Final

from google.cloud import tasks_v2
from google.cloud.storage import Client
from openai import OpenAI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from adapter.adapter import StorageAdapter, TaskQueueAdapter, LogAdapter, OpenaiAdapter, UserRepository, \
    DocumentRepository, OpenaiAssistantRepository
from config.envs import DATABASE_URL
from config.envs import OPENAI_API_KEY
from infra.cloud_sql.document_repo import DocumentRepoImpl
from infra.cloud_sql.openai_assistant_repo import OpenaiAssistantRepoImpl
from infra.cloud_sql.user_repo import UserRepoImpl
from infra.cloud_storage import CloudStorageImpl
from infra.cloud_tasks import CloudTasksImpl
from infra.logger import LoggerImpl
from infra.openai import OpenaiImpl

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

storage_adapter: Final[StorageAdapter] = CloudStorageImpl.new(Client())
task_queue_adapter: Final[TaskQueueAdapter] = CloudTasksImpl.new(
    tasks_v2.CloudTasksClient()
)
log_adapter: Final[LogAdapter] = LoggerImpl.new()
openai_adapter: Final[OpenaiAdapter] = OpenaiImpl.new(
    OpenAI(
        api_key=OPENAI_API_KEY,
    )
)
user_repository: Final[UserRepository] = UserRepoImpl.new(Session)
document_repository: Final[DocumentRepository] = DocumentRepoImpl.new(Session)
openai_assistant_repository: Final[OpenaiAssistantRepository] = OpenaiAssistantRepoImpl.new(Session)
