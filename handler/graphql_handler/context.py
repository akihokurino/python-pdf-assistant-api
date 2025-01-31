import dataclasses
from functools import cached_property

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from strawberry.fastapi import BaseContext

from adapter.adapter import UserRepository, DocumentRepository
from di.di import AppContainer
from domain.error import AppError
from domain.user import User
from handler.auth import verify


@dataclasses.dataclass
class Context(BaseContext):
    user_repo: UserRepository
    document_repo: DocumentRepository

    @cached_property
    async def login_user(self) -> User | None:
        if not self.request:
            return None

        token = self.request.headers.get("Authorization", None)
        try:
            user_id = verify(token)
            user = await self.user_repo.get(user_id)
            return user
        except AppError:
            return None


@inject
async def get_context(
    user_repo: UserRepository = Depends(Provide[AppContainer.user_repository]),
    document_repo: DocumentRepository = Depends(
        Provide[AppContainer.document_repository]
    ),
) -> Context:
    return Context(user_repo=user_repo, document_repo=document_repo)
