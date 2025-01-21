from typing import Callable, Awaitable, final

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from di.di import log_adapter
from model.error import AppError


@final
class ErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(
            self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        try:
            response: Response = await call_next(request)
        except AppError as e:
            log_adapter.log_error(e)
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
            log_adapter.log_error(e)
            response = JSONResponse(
                {"message": "サーバーエラーが発生しました"},
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return response
