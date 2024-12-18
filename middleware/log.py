from functools import wraps
from typing import Callable, TypeVar, Any, cast

LogMiddleware = TypeVar("LogMiddleware", bound=Callable[..., Any])


def log_middleware(f: LogMiddleware) -> LogMiddleware:
    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        return f(*args, **kwargs)

    return cast(LogMiddleware, decorated)
