import strawberry

from domain.user import UserId
from handler.graphql_handler.context import Context
from handler.graphql_handler.response import User


@strawberry.type  # type: ignore
class Query:
    @strawberry.field
    async def user(self, info: strawberry.Info) -> User:
        context: Context = info.context
        user = await context.user_repo.get(
            _id=UserId("yqkYZa7SJoaVEgBX3XKxzwaryg93gv7x@clients")
        )
        if user is None:
            raise ValueError("User not found")
        print(user.name)
        return User(name=user.name, age=22)
