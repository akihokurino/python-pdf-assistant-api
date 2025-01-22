from dependency_injector import containers, providers
from dependency_injector.providers import Singleton
from google.cloud import storage
from google.cloud import tasks_v2
from openai import OpenAI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from adapter.adapter import StorageAdapter, UserRepository, DocumentRepository, OpenaiAssistantRepository, \
    OpenaiAdapter, LogAdapter, TaskQueueAdapter
from config.envs import DATABASE_URL
from config.envs import OPENAI_API_KEY
from infra.cloud_sql.document_repo import DocumentRepoImpl
from infra.cloud_sql.openai_assistant_repo import OpenaiAssistantRepoImpl
from infra.cloud_sql.user_repo import UserRepoImpl
from infra.cloud_storage import CloudStorageImpl
from infra.cloud_tasks import CloudTasksImpl
from infra.logger import LoggerImpl
from infra.openai import OpenaiImpl


class AppContainer(containers.DeclarativeContainer):
    database_url = providers.Object(DATABASE_URL)
    openai_api_key = providers.Object(OPENAI_API_KEY)
    engine = providers.Singleton(create_engine, database_url)
    session = providers.Singleton(sessionmaker, bind=engine)
    cloud_storage_client: Singleton[storage.Client] = providers.Singleton(storage.Client)
    cloud_tasks_client: Singleton[tasks_v2.CloudTasksClient] = providers.Singleton(tasks_v2.CloudTasksClient)
    openai_client: Singleton[OpenAI] = providers.Singleton(OpenAI, api_key=openai_api_key)

    storage_adapter: Singleton[StorageAdapter] = providers.Singleton(
        CloudStorageImpl.new, cloud_storage_client
    )
    task_queue_adapter: Singleton[TaskQueueAdapter] = providers.Singleton(
        CloudTasksImpl.new, cloud_tasks_client
    )
    log_adapter: Singleton[LogAdapter] = providers.Singleton(LoggerImpl.new)
    openai_adapter: Singleton[OpenaiAdapter] = providers.Singleton(OpenaiImpl.new, openai_client)

    user_repository: Singleton[UserRepository] = providers.Singleton(UserRepoImpl.new, session)
    document_repository: Singleton[DocumentRepository] = providers.Singleton(DocumentRepoImpl.new, session)
    openai_assistant_repository: Singleton[OpenaiAssistantRepository] = providers.Singleton(
        OpenaiAssistantRepoImpl.new, session
    )


container = AppContainer()


## FastAPIに依存注入する場合の型チェック用
def use_storage() -> StorageAdapter:
    return container.storage_adapter()


def use_task_queue() -> TaskQueueAdapter:
    return container.task_queue_adapter()


def use_log() -> LogAdapter:
    return container.log_adapter()


def use_openai() -> OpenaiAdapter:
    return container.openai_adapter()


def use_user_repo() -> UserRepository:
    return container.user_repository()


def use_document_repo() -> DocumentRepository:
    return container.document_repository()


def use_openai_assistant_repo() -> OpenaiAssistantRepository:
    return container.openai_assistant_repository()
