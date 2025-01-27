import base64
import json
from typing import Callable, Optional, Awaitable, final

from auth0.authentication.token_verifier import (
    TokenVerifier,
    AsymmetricSignatureVerifier,
    TokenValidationError,
)
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from config.envs import TASK_QUEUE_TOKEN
from domain.error import AppError, ErrorKind
from domain.user import UserId

AUTH0_ISSUER = "https://dev-im6sd3gmyj703h6n.us.auth0.com/"
AUTH0_JWKS_URL = "https://dev-im6sd3gmyj703h6n.us.auth0.com/.well-known/jwks.json"
AUTH0_AUDIENCE = "https://api-gateway-7nwm7l18.an.gateway.dev"

NO_AUTH_PATH = ["/debug", "/subscriber/storage_upload_notification"]


@final
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
            self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if request.url.path in NO_AUTH_PATH:
            response: Response = await call_next(request)
            return response

        task_queue_token: Optional[str] = request.headers.get("x-queue-token")
        if task_queue_token and task_queue_token == TASK_QUEUE_TOKEN:
            response = await call_next(request)
            return response

        user_info_encoded: Optional[str] = request.headers.get(
            "X-Apigateway-Api-Userinfo"
        )
        if user_info_encoded:
            # ApiGatewayからのユーザ情報をデコード
            decoded_bytes = base64.urlsafe_b64decode(user_info_encoded + "===")
            decoded_payload = json.loads(decoded_bytes.decode("utf-8"))

            request.state.uid = decoded_payload.get("sub")
        else:
            # ローカルでトークンを解析
            token: Optional[str] = request.headers.get("Authorization")
            if not token or not token.startswith("Bearer "):
                raise AppError(ErrorKind.UNAUTHORIZED, "認証エラーです")
            raw_token: str = token.split("Bearer ")[1]

            try:
                sv = AsymmetricSignatureVerifier(AUTH0_JWKS_URL)
                tv = TokenVerifier(
                    signature_verifier=sv,
                    issuer=AUTH0_ISSUER,
                    audience=AUTH0_AUDIENCE,
                )
                decoded_token = tv.verify(raw_token)
            except TokenValidationError as e:
                raise AppError(ErrorKind.UNAUTHORIZED, "認証エラーです") from e
            except Exception as e:
                raise e

            user_id: Optional[UserId] = decoded_token.get("sub")
            if not user_id:
                raise AppError(ErrorKind.UNAUTHORIZED, "認証エラーです")

            request.state.uid = user_id

        response = await call_next(request)
        return response
