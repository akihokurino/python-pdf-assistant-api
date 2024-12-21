import json
from typing import Callable, Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from infra.logger import log_info


class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[..., Any]
    ) -> Response:
        log_info("------------------------------------------------------")
        log_info(f"Request Endpoint: {request.url.path}")
        for k, v in request.headers.items():
            log_info(f"Request Header: {k}={v}")

        try:
            body = await request.json()
            log_info(f"Request Body: {body}")
        except json.JSONDecodeError:
            log_info("Request Body is not valid JSON or is empty.")
        except Exception as e:
            log_info(f"Error reading request body: {e}")

        response: Response = await call_next(request)

        log_info(f"Response Status: {response.status_code}")
        log_info("------------------------------------------------------")

        return response
