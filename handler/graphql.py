import pkgutil
from contextlib import asynccontextmanager
from typing import Final, Any, AsyncGenerator

import strawberry
import uvicorn
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from di.di import container
from handler import graphql_handler
from handler.graphql_handler.context import get_context
from handler.graphql_handler.query import Query


@asynccontextmanager
async def _lifespan(_app: FastAPI) -> AsyncGenerator[None, Any]:
    modules = [
        f"handler.graphql_handler.{name}"
        for _, name, _ in pkgutil.iter_modules(graphql_handler.__path__)
    ]
    container.wire(modules=modules)
    _app.container = container  # type: ignore
    yield


app: Final[FastAPI] = FastAPI(lifespan=_lifespan)
schema: Final = strawberry.Schema(query=Query)
app.include_router(GraphQLRouter(schema, context_getter=get_context), prefix="/graphql")


def start() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="debug")
