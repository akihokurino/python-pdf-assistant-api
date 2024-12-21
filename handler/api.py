from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from handler.response import user_response
from infra.cloud_sql.user import get_user, insert_user
from middleware.auth import AuthMiddleware
from middleware.error import ErrorMiddleware
from middleware.log import LogMiddleware
from model.user import User

app = FastAPI()
app.add_middleware(AuthMiddleware)
app.add_middleware(LogMiddleware)
app.add_middleware(ErrorMiddleware)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "message": "不正なリクエストです",
            "detail": exc.errors(),
        },
    )


def start() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="debug")


class CreateUserPayload(BaseModel):
    name: str


@app.post("/users")
def create_user(
    request: Request,
    payload: CreateUserPayload,
) -> JSONResponse:
    uid = request.state.uid
    now = datetime.utcnow()
    user = get_user(uid)
    if user:
        return JSONResponse(content=user_response(user), status_code=200)
    new_user = User(uid, payload.name, now)
    insert_user(new_user)
    return JSONResponse(content=user_response(new_user), status_code=200)
