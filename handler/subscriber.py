from typing import Final, final

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from infra.logger import log_info

router: Final[APIRouter] = APIRouter()


@final
class _CreateOpenaiAssistantPayload(BaseModel):
    document_id: str


@router.post("/subscriber/create_openai_assistant")
def _create_openai_assistant(
    request: Request,
    payload: _CreateOpenaiAssistantPayload,
) -> JSONResponse:
    log_info("create_openai_assistant!!")
    log_info(payload.document_id)

    return JSONResponse(
        content={},
        status_code=200,
    )
