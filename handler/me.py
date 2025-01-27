from typing import Final

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Request, Depends

from adapter.adapter import UserRepository
from di.di import AppContainer
from domain.error import AppError, ErrorKind
from domain.user import UserId
from handler.response import MeResp

router: Final[APIRouter] = APIRouter()


@router.get("/me")
@inject
async def _me(
        request: Request,
        user_repository: UserRepository = Depends(Provide[AppContainer.user_repository]),
) -> MeResp:
    uid: Final[UserId] = request.state.uid

    result: Final = await user_repository.get_with_documents(uid)
    if not result:
        raise AppError(ErrorKind.NOT_FOUND, f"ユーザーが見つかりません: {uid}")

    return MeResp.from_model(result[0], result[1])
