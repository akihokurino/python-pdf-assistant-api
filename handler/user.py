from datetime import datetime, timezone
from typing import final, Final

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel

from adapter.adapter import UserRepository
from di.di import AppContainer
from domain.error import AppError, ErrorKind
from domain.user import User, UserId
from handler.response import UserResp

router: Final[APIRouter] = APIRouter()


@final
class _CreateUserPayload(BaseModel):
    name: str


@router.post("/users")
@inject
async def _create_user(
        request: Request,
        payload: _CreateUserPayload,
        user_repository: UserRepository = Depends(Provide[AppContainer.user_repository]),
) -> UserResp:
    uid: Final[UserId] = request.state.uid
    now: Final = datetime.now(timezone.utc)

    already: Final = await user_repository.get(uid)
    if already:
        return UserResp.from_model(already)

    new_user: Final = User.new(uid, payload.name, now)
    await user_repository.insert(new_user)

    return UserResp.from_model(new_user)


@final
class _UpdateUserPayload(BaseModel):
    name: str


@router.put("/users")
@inject
async def _update_user(
        request: Request,
        payload: _UpdateUserPayload,
        user_repository: UserRepository = Depends(Provide[AppContainer.user_repository]),
) -> UserResp:
    uid: Final[UserId] = request.state.uid
    now: Final = datetime.now(timezone.utc)

    user: Final = await user_repository.get(uid)
    if not user:
        raise AppError(ErrorKind.NOT_FOUND, f"ユーザーが見つかりません: {uid}")

    user.update(payload.name, now)
    await user_repository.update(user)

    return UserResp.from_model(user)
