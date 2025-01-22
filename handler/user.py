from datetime import datetime, timezone
from typing import final, Final

from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from adapter.adapter import UserRepository
from handler.response import user_resp
from model.error import AppError, ErrorKind
from model.user import User, UserId

router: Final[APIRouter] = APIRouter()


@final
class _CreateUserPayload(BaseModel):
    name: str


@router.post("/users")
def _create_user(
        request: Request,
        payload: _CreateUserPayload,
        user_repository: UserRepository = Depends(),
) -> JSONResponse:
    uid: Final[UserId] = request.state.uid
    now: Final[datetime] = datetime.now(timezone.utc)

    user = user_repository.get_user(uid)
    if user:
        return JSONResponse(content=user_resp(user), status_code=200)

    new_user = User.new(uid, payload.name, now)
    user_repository.insert_user(new_user)

    return JSONResponse(content=user_resp(new_user), status_code=200)


@final
class _UpdateUserPayload(BaseModel):
    name: str


@router.put("/users")
def _update_user(
        request: Request,
        payload: _UpdateUserPayload,
        user_repository: UserRepository = Depends(),
) -> JSONResponse:
    uid: Final[UserId] = request.state.uid
    now: Final[datetime] = datetime.now(timezone.utc)

    user = user_repository.get_user(uid)
    if not user:
        raise AppError(ErrorKind.NOT_FOUND, f"ユーザーが見つかりません: {uid}")

    user.update(payload.name, now)
    user_repository.update_user(user)

    return JSONResponse(content=user_resp(user), status_code=200)
