from typing import Optional

from auth0.authentication.token_verifier import (
    TokenVerifier,
    AsymmetricSignatureVerifier,
    TokenValidationError,
)

from domain.error import AppError, ErrorKind
from domain.user import UserId

AUTH0_ISSUER = "https://dev-im6sd3gmyj703h6n.us.auth0.com/"
AUTH0_JWKS_URL = "https://dev-im6sd3gmyj703h6n.us.auth0.com/.well-known/jwks.json"
AUTH0_AUDIENCE = "https://api-gateway-7nwm7l18.an.gateway.dev"


def verify(token: Optional[str]) -> UserId:
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

    return user_id
