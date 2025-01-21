from typing import Final

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from di.di import user_repository
from handler.response import user_resp, document_resp
from model.error import AppError, ErrorKind
from model.user import UserId

router: Final[APIRouter] = APIRouter()


@router.get("/me")
def _me(
        request: Request,
) -> JSONResponse:
    uid: Final[UserId] = request.state.uid

    result = user_repository.get_user_with_documents(uid)
    if not result:
        raise AppError(ErrorKind.NOT_FOUND, f"ユーザーが見つかりません: {uid}")

    return JSONResponse(
        content={
            "user": user_resp(result[0]),
            "documents": [document_resp(doc) for doc in result[1]],
        },
        status_code=200,
    )
