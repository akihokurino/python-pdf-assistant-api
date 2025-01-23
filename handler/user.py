from datetime import datetime, timezone
from typing import final, Final

from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel

from adapter.adapter import UserRepository
from handler.response import UserResp
from model.error import AppError, ErrorKind
from model.user import User, UserId

router: Final[APIRouter] = APIRouter()


@final
class _CreateUserPayload(BaseModel):
    name: str


@router.post("/users")
async def _create_user(
        request: Request,
        payload: _CreateUserPayload,
        user_repository: UserRepository = Depends(),
) -> UserResp:
    uid: Final[UserId] = request.state.uid
    now: Final[datetime] = datetime.now(timezone.utc)

    user = await user_repository.get_user(uid)
    if user:
        return UserResp.from_model(user)

    new_user = User.new(uid, payload.name, now)
    await user_repository.insert_user(new_user)

    return UserResp.from_model(new_user)


@final
class _UpdateUserPayload(BaseModel):
    name: str


@router.put("/users")
async def _update_user(
        request: Request,
        payload: _UpdateUserPayload,
        user_repository: UserRepository = Depends(),
) -> UserResp:
    uid: Final[UserId] = request.state.uid
    now: Final[datetime] = datetime.now(timezone.utc)

    user = await user_repository.get_user(uid)
    if not user:
        raise AppError(ErrorKind.NOT_FOUND, f"ユーザーが見つかりません: {uid}")

    user.update(payload.name, now)
    await user_repository.update_user(user)

    return UserResp.from_model(user)
