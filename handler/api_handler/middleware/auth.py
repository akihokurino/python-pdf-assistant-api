import base64
import json
from typing import Callable, Optional, Awaitable, final

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from config.envs import TASK_QUEUE_TOKEN
from handler.auth import verify

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
            user_id = verify(token)
            request.state.uid = user_id

        response = await call_next(request)
        return response
