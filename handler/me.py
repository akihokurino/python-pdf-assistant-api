from typing import Final

from fastapi import APIRouter, Request, Depends

from adapter.adapter import UserRepository
from handler.response import MeResp
from model.error import AppError, ErrorKind
from model.user import UserId

router: Final[APIRouter] = APIRouter()


@router.get("/me")
async def _me(
        request: Request,
        user_repository: UserRepository = Depends(),
) -> MeResp:
    uid: Final[UserId] = request.state.uid

    result = user_repository.get_user_with_documents(uid)
    if not result:
        raise AppError(ErrorKind.NOT_FOUND, f"ユーザーが見つかりません: {uid}")

    return MeResp.from_model(result[0], result[1])
