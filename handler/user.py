from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from handler.response import user_response
from infra.cloud_sql.user import (
    get_user,
    insert_user,
    update_user,
)
from model.error import AppError, ErrorKind
from model.user import User

router = APIRouter()


class _CreateUserPayload(BaseModel):
    name: str


@router.post("/users")
def _create_user(
    request: Request,
    payload: _CreateUserPayload,
) -> JSONResponse:
    uid = request.state.uid
    now = datetime.utcnow()

    user = get_user(uid)
    if user:
        return JSONResponse(content=user_response(user), status_code=200)

    new_user = User.new(uid, payload.name, now)
    insert_user(new_user)

    return JSONResponse(content=user_response(new_user), status_code=200)


class _UpdateUserPayload(BaseModel):
    name: str


@router.put("/users")
def _update_user(
    request: Request,
    payload: _UpdateUserPayload,
) -> JSONResponse:
    uid = request.state.uid
    now = datetime.utcnow()

    user = get_user(uid)
    if not user:
        raise AppError(ErrorKind.NOT_FOUND, f"ユーザーが見つかりません: {uid}")

    user.update(payload.name, now)
    update_user(user)

    return JSONResponse(content=user_response(user), status_code=200)
