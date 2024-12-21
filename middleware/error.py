from typing import Callable, Any

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from model.error import AppError


class ErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[..., Any]
    ) -> Response:
        try:
            response: Response = await call_next(request)
        except AppError as e:
            response = JSONResponse(
                {"message": e.message},
                e.kind.value,
            )
        except TimeoutError as e:
            response = JSONResponse(
                {"message": "タイムアウトエラーが発生しました。"},
                status.HTTP_408_REQUEST_TIMEOUT,
            )
        except Exception as e:
            response = JSONResponse(
                {"message": "サーバーエラーが発生しました"},
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return response
