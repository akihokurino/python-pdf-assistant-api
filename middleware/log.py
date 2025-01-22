import json
from typing import Callable, Awaitable, final

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from adapter.adapter import LogAdapter
from di.di import container


@final
class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(
            self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        log_adapter: LogAdapter = container.log_adapter()

        log_adapter.log_info("------------------------------------------------------")
        log_adapter.log_info(f"Request Endpoint: {request.url.path}")
        for k, v in request.headers.items():
            log_adapter.log_info(f"Request Header: {k}={v}")

        try:
            body = await request.json()
            log_adapter.log_info(f"Request Body: {body}")
        except json.JSONDecodeError:
            log_adapter.log_info("Request Body is not valid JSON or is empty.")
        except Exception as e:
            log_adapter.log_info(f"Error reading request body: {e}")

        response: Response = await call_next(request)

        log_adapter.log_info(f"Response Status: {response.status_code}")
        log_adapter.log_info("------------------------------------------------------")

        return response
