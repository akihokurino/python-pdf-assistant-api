from typing import Generator, Optional

from graphql.error import GraphQLError
from strawberry.extensions import SchemaExtension

from domain.error import AppError


class ErrorExtension(SchemaExtension):
    def on_execute(self) -> Generator[None, None, None]:
        yield

        errors: Optional[list[GraphQLError]] = self.execution_context.errors
        if errors is None:
            return

        for error in errors:
            original_error = error.original_error

            if isinstance(original_error, AppError):
                if error.extensions is None:
                    error.extensions = {}
                error.extensions["code"] = original_error.kind.name
