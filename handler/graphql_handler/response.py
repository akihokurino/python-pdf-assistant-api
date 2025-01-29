import strawberry


@strawberry.type  # type: ignore
class User:
    name: str
    age: int
