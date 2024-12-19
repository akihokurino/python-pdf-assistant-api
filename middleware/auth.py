from functools import wraps
from typing import Callable, TypeVar, Any, cast, Optional

from auth0.authentication.token_verifier import (
    TokenVerifier,
    AsymmetricSignatureVerifier,
    TokenValidationError,
)
from flask import request, g

from infra.logger import log_info
from model.error import AppError, ErrorKind

AUTH0_ISSUER = "https://dev-im6sd3gmyj703h6n.us.auth0.com/"
AUTH0_JWKS_URL = "https://dev-im6sd3gmyj703h6n.us.auth0.com/.well-known/jwks.json"
AUTH0_AUDIENCE = "https://api-gateway-a55kw77s.an.gateway.dev"

AuthMiddleware = TypeVar("AuthMiddleware", bound=Callable[..., Any])


def auth_middleware(f: AuthMiddleware) -> AuthMiddleware:
    """認証用ミドルウェア"""

    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        try:
            token: Optional[str] = request.headers.get("Authorization")
            if not token:
                raise AppError(ErrorKind.UNAUTHORIZED, "認証エラーです")
            if not token.startswith("Bearer "):
                raise AppError(ErrorKind.UNAUTHORIZED, "認証エラーです")

            raw_token: str = token.split("Bearer ")[1]

            log_info(raw_token)

            sv = AsymmetricSignatureVerifier(AUTH0_JWKS_URL)
            tv = TokenVerifier(
                signature_verifier=sv,
                issuer=AUTH0_ISSUER,
                audience=AUTH0_AUDIENCE,
            )
            decoded_token = tv.verify(raw_token)

            user_id: Optional[str] = decoded_token.get("sub")
            if not user_id:
                raise AppError(ErrorKind.UNAUTHORIZED, "認証エラーです")
            g.uid = user_id

            return f(*args, **kwargs)
        except AppError as e:
            return e.error_response()
        except TokenValidationError as e:
            return AppError(
                ErrorKind.UNAUTHORIZED, f"トークンの検証に失敗しました: {e}"
            ).error_response()
        except Exception as e:
            return AppError(
                ErrorKind.INTERNAL, f"エラーが発生しました: {e}"
            ).error_response()

    return cast(AuthMiddleware, decorated)
