import strawberry

from domain.error import AppError, ErrorKind
from handler.graphql_handler.context import Context
from handler.graphql_handler.response import MeResp


@strawberry.type  # type: ignore
class Query:
    @strawberry.field
    async def me(self, info: strawberry.Info[Context]) -> MeResp:
        context: Context = info.context
        me = await context.login_user
        if me is None:
            raise AppError(ErrorKind.UNAUTHORIZED)
        return MeResp.from_model(me)
