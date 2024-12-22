import uuid
from typing import Final

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from infra.cloud_storage import generate_pre_signed_upload_url

router: Final[APIRouter] = APIRouter()


@router.get("/documents/pre_signed_upload_url")
def _pre_signed_upload_url(
    request: Request,
) -> JSONResponse:
    uid: Final[str] = request.state.uid
    blob_name = f"documents/{uid}/{uuid.uuid4()}.pdf"
    url = generate_pre_signed_upload_url(blob_name)

    return JSONResponse(
        content={
            "url": url,
            "key": blob_name,
        },
        status_code=200,
    )
