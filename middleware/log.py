import logging
from functools import wraps
from typing import Callable, TypeVar, Any, cast

from flask import request, Response

LogMiddleware = TypeVar("LogMiddleware", bound=Callable[..., Any])
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def log_middleware(f: LogMiddleware) -> LogMiddleware:
    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        logger.info("------------------------------------------------------")
        logger.info(f"Request Endpoint: {request.path}")
        if request.is_json:
            logger.info(f"Request Body: {request.get_json()}")

        response = f(*args, **kwargs)

        if isinstance(response, tuple) and len(response) == 2:
            body, status = response
            if isinstance(body, Response) and body.mimetype == "application/json":
                logger.info(f"Response Body: {body.get_data(as_text=True)}")
            logger.info(f"Response Status: {status}")
        logger.info("------------------------------------------------------")

        return response

    return cast(LogMiddleware, decorated)
