from dependency_injector import containers, providers
from dependency_injector.providers import Singleton
from google.cloud import storage
from google.cloud import tasks_v2
from google.cloud.firestore import AsyncClient
from openai import OpenAI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from adapter.adapter import (
    StorageAdapter,
    UserRepository,
    DocumentRepository,
    OpenaiAssistantRepository,
    OpenaiAdapter,
    LogAdapter,
    TaskQueueAdapter,
    OpenaiAssistantFSRepository, OpenaiMessageFSRepository,
)
from config.envs import DATABASE_URL
from config.envs import OPENAI_API_KEY
from infra.cloud_sql.document_repo import DocumentRepoImpl
from infra.cloud_sql.openai_assistant_repo import OpenaiAssistantRepoImpl
from infra.cloud_sql.user_repo import UserRepoImpl
from infra.cloud_storage import CloudStorageImpl
from infra.cloud_tasks import CloudTasksImpl
from infra.datastore.openai_assistant_repo import OpenaiAssistantFSRepoImpl
from infra.datastore.openai_message_repo import OpenaiMessageFSRepoImpl
from infra.logger import LoggerImpl
from infra.openai import OpenaiImpl


class AppContainer(containers.DeclarativeContainer):
    database_url = providers.Object(DATABASE_URL)
    openai_api_key = providers.Object(OPENAI_API_KEY)
    engine = providers.Singleton(create_async_engine, database_url)
    session = providers.Singleton(async_sessionmaker, bind=engine)
    
    cloud_storage_client: Singleton[storage.Client] = providers.Singleton(
        storage.Client
    )
    cloud_tasks_client: Singleton[tasks_v2.CloudTasksClient] = providers.Singleton(
        tasks_v2.CloudTasksClient
    )
    openai_client: Singleton[OpenAI] = providers.Singleton(
        OpenAI, api_key=openai_api_key
    )
    firestore: Singleton[AsyncClient] = providers.Singleton(AsyncClient, database="pdf-assistant")

    storage_adapter: Singleton[StorageAdapter] = providers.Singleton(
        CloudStorageImpl.new, cloud_storage_client
    )
    task_queue_adapter: Singleton[TaskQueueAdapter] = providers.Singleton(
        CloudTasksImpl.new, cloud_tasks_client
    )
    log_adapter: Singleton[LogAdapter] = providers.Singleton(LoggerImpl.new)
    openai_adapter: Singleton[OpenaiAdapter] = providers.Singleton(
        OpenaiImpl.new, openai_client
    )

    user_repository: Singleton[UserRepository] = providers.Singleton(
        UserRepoImpl.new, session
    )
    document_repository: Singleton[DocumentRepository] = providers.Singleton(
        DocumentRepoImpl.new, session
    )
    openai_assistant_repository: Singleton[OpenaiAssistantRepository] = (
        providers.Singleton(OpenaiAssistantRepoImpl.new, session)
    )

    openai_assistant_fs_repository: Singleton[OpenaiAssistantFSRepository] = (
        providers.Singleton(OpenaiAssistantFSRepoImpl.new, firestore)
    )
    openai_message_fs_repository: Singleton[OpenaiMessageFSRepository] = (
        providers.Singleton(OpenaiMessageFSRepoImpl.new, firestore)
    )


container = AppContainer()
