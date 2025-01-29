import dataclasses

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from strawberry.fastapi import BaseContext

from adapter.adapter import UserRepository
from di.di import AppContainer


@dataclasses.dataclass
class Context(BaseContext):
    user_repo: UserRepository


@inject
async def get_context(
    user_repo: UserRepository = Depends(Provide[AppContainer.user_repository]),
) -> Context:
    return Context(user_repo=user_repo)
