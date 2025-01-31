from __future__ import annotations

from datetime import datetime

import strawberry

from domain.user import User, UserId
from handler.graphql_handler.context import Context
from handler.graphql_handler.document import DocumentResp


async def resolve_documents(
    parent: strawberry.Parent[UserResp], info: strawberry.Info[Context]
) -> list[DocumentResp]:
    context: Context = info.context
    documents = await context.document_repo.find_by_user(UserId(parent.id))
    return [DocumentResp.from_model(doc) for doc in documents]


@strawberry.type
class UserResp:
    id: str
    name: str
    created_at: datetime
    updated_at: datetime
    documents: list[DocumentResp] = strawberry.field(resolver=resolve_documents)

    @classmethod
    def from_model(cls, user: User) -> UserResp:
        return cls(
            id=user.id,
            name=user.name,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
