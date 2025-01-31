import strawberry

from domain.document import DocumentId
from domain.error import AppError, ErrorKind
from domain.user import UserId
from handler.graphql_handler.context import Context
from handler.graphql_handler.document import DocumentResp
from handler.graphql_handler.response import MeResp, UserResp


@strawberry.type  # type: ignore
class Query:
    @strawberry.field
    async def me(self, info: strawberry.Info[Context]) -> MeResp:
        context: Context = info.context
        me = await context.login_user
        if me is None:
            raise AppError(ErrorKind.UNAUTHORIZED)
        return MeResp.from_model(me)

    @strawberry.field
    async def user(self, info: strawberry.Info[Context], id: strawberry.ID) -> UserResp:
        context: Context = info.context
        me = await context.login_user
        if me is None:
            raise AppError(ErrorKind.UNAUTHORIZED)

        if id is None:
            raise AppError(ErrorKind.BAD_REQUEST)

        user = await context.user_repo.get(UserId(id))
        if user is None:
            raise AppError(ErrorKind.NOT_FOUND)
        return UserResp.from_model(user)

    @strawberry.field
    async def document(
        self, info: strawberry.Info[Context], id: strawberry.ID
    ) -> DocumentResp:
        context: Context = info.context
        me = await context.login_user
        if me is None:
            raise AppError(ErrorKind.UNAUTHORIZED)

        if id is None:
            raise AppError(ErrorKind.BAD_REQUEST)

        document = await context.document_repo.get(DocumentId(id))
        if document is None:
            raise AppError(ErrorKind.NOT_FOUND)
        if document.user_id != me.id:
            raise AppError(ErrorKind.FORBIDDEN)
        return DocumentResp.from_model(document)
