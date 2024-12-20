import json
from typing import Final, Tuple

from flask import Flask, Response, g
from flask_cors import CORS

from infra.logger import log_info
from middleware.auth import auth_middleware
from middleware.log import log_middleware

app: Final[Flask] = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
CORS(app)


def start() -> None:
    app.run(host="0.0.0.0", port=8080, debug=True)


@app.route("/hello", methods=["POST"])
@log_middleware
@auth_middleware
def hello() -> Tuple[Response, int]:
    uid = g.uid
    log_info(f"uid: {uid}")

    json_data = json.dumps({"message": "hello world"}, ensure_ascii=False, indent=4)
    return Response(json_data, mimetype="application/json"), 200
