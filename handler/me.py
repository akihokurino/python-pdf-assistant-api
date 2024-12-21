from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from handler.response import user_response
from infra.cloud_sql.user import get_user
from model.error import AppError, ErrorKind

router = APIRouter()


@router.get("/me")
def _me(
    request: Request,
) -> JSONResponse:
    uid = request.state.uid

    user = get_user(uid)
    if not user:
        raise AppError(ErrorKind.NOT_FOUND, f"ユーザーが見つかりません: {uid}")

    return JSONResponse(content=user_response(user), status_code=200)
