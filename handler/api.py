from datetime import datetime
from typing import Final, Tuple

from flask import Flask, Response, g
from flask_cors import CORS

from handler.response import user_response, ok
from infra.cloud_sql.user import get_user, insert_user
from middleware.auth import auth_middleware
from middleware.log import log_middleware
from model.error import AppError, ErrorKind
from model.user import User

app: Final[Flask] = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
CORS(app)


def start() -> None:
    app.run(host="0.0.0.0", port=8080, debug=True)


@app.route("/users", methods=["POST"])
@log_middleware
@auth_middleware
def create_user() -> Tuple[Response, int]:
    uid = g.uid
    now = datetime.utcnow()
    try:
        user = get_user(uid)
        if user:
            return ok(user_response(user))
        new_user = User(uid, "user", now)
        insert_user(new_user)
        return ok(user_response(new_user))
    except AppError as e:
        return e.error_response()
    except Exception as e:
        return AppError(
            ErrorKind.INTERNAL, f"エラーが発生しました: {e}"
        ).error_response()
