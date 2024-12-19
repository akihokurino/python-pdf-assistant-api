from functools import wraps
from typing import Callable, TypeVar, Any, cast

from flask import request, Response

from infra.logger import log_info

LogMiddleware = TypeVar("LogMiddleware", bound=Callable[..., Any])


def log_middleware(f: LogMiddleware) -> LogMiddleware:
    """ログ用ミドルウェア"""

    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        log_info("------------------------------------------------------")
        log_info(f"Request Endpoint: {request.path}")
        if request.is_json:
            log_info(f"Request Body: {request.get_json()}")

        response = f(*args, **kwargs)

        if isinstance(response, tuple) and len(response) == 2:
            body, status = response
            if isinstance(body, Response) and body.mimetype == "application/json":
                log_info(f"Response Body: {body.get_data(as_text=True)}")
            log_info(f"Response Status: {status}")
        log_info("------------------------------------------------------")

        return response

    return cast(LogMiddleware, decorated)
