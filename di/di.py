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
    AssistantRepository,
    OpenAIAdapter,
    LogAdapter,
    TaskQueueAdapter,
    AssistantFSRepository,
    MessageFSRepository,
    DocumentSummaryRepository,
)
from config.envs import DATABASE_URL
from config.envs import OPENAI_API_KEY
from infra.cloud_sql.assistant_repo import AssistantRepoImpl
from infra.cloud_sql.document_repo import DocumentRepoImpl
from infra.cloud_sql.document_summary_repo import DocumentSummaryRepoImpl
from infra.cloud_sql.user_repo import UserRepoImpl
from infra.cloud_storage import CloudStorageImpl, AsyncCloudStorageImpl
from infra.cloud_tasks import CloudTasksImpl, AsyncCloudTasksImpl
from infra.firestore.assistant_repo import AssistantFSRepoImpl
from infra.firestore.message_repo import MessageFSRepoImpl
from infra.logger import LoggerImpl
from infra.openai import OpenAIImpl, AsyncOpenAIImpl


class AppContainer(containers.DeclarativeContainer):
    __database_url = providers.Object(DATABASE_URL)
    __openai_api_key = providers.Object(OPENAI_API_KEY)
    __engine = providers.Singleton(create_async_engine, __database_url)
    __session = providers.Singleton(async_sessionmaker, bind=__engine)
    __cloud_storage_client: Singleton[storage.Client] = providers.Singleton(
        storage.Client
    )
    __cloud_tasks_client: Singleton[tasks_v2.CloudTasksClient] = providers.Singleton(
        tasks_v2.CloudTasksClient
    )
    __openai_client: Singleton[OpenAI] = providers.Singleton(
        OpenAI, api_key=__openai_api_key
    )
    __firestore: Singleton[AsyncClient] = providers.Singleton(
        AsyncClient, database="pdf-assistant"
    )
    __cloud_storage_impl: Singleton[CloudStorageImpl] = providers.Singleton(
        CloudStorageImpl, cli=__cloud_storage_client
    )
    __cloud_tasks_impl: Singleton[CloudTasksImpl] = providers.Singleton(
        CloudTasksImpl, cli=__cloud_tasks_client
    )
    __openai_impl: Singleton[OpenAIImpl] = providers.Singleton(
        OpenAIImpl, cli=__openai_client
    )

    # Adapters
    log_adapter: Singleton[LogAdapter] = providers.Singleton(LoggerImpl.new)
    storage_adapter: Singleton[StorageAdapter] = providers.Singleton(
        AsyncCloudStorageImpl.new, inner=__cloud_storage_impl
    )
    task_queue_adapter: Singleton[TaskQueueAdapter] = providers.Singleton(
        AsyncCloudTasksImpl.new, inner=__cloud_tasks_impl
    )
    openai_adapter: Singleton[OpenAIAdapter] = providers.Singleton(
        AsyncOpenAIImpl.new, inner=__openai_impl
    )

    # Repositories
    user_repository: Singleton[UserRepository] = providers.Singleton(
        UserRepoImpl.new, __session
    )
    document_repository: Singleton[DocumentRepository] = providers.Singleton(
        DocumentRepoImpl.new, __session
    )
    document_summary_repository: Singleton[DocumentSummaryRepository] = (
        providers.Singleton(DocumentSummaryRepoImpl.new, __session)
    )
    assistant_repository: Singleton[AssistantRepository] = providers.Singleton(
        AssistantRepoImpl.new, __session
    )
    assistant_fs_repository: Singleton[AssistantFSRepository] = providers.Singleton(
        AssistantFSRepoImpl.new, __firestore
    )
    message_fs_repository: Singleton[MessageFSRepository] = providers.Singleton(
        MessageFSRepoImpl.new, __firestore
    )


container = AppContainer()
