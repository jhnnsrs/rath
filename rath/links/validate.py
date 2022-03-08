from typing import AsyncIterator
from graphql import (
    GraphQLSchema,
    build_ast_schema,
    build_schema,
    get_introspection_query,
    validate,
)
from graphql.language.parser import parse
from rath.links.base import ContinuationLink
from rath.links.errors import ContinuationLinkError
from rath.operation import GraphQLResult, Operation, opify
from .parsing import ParsingLink
from glob import glob


def schemify(
    schema_dsl: str = None, schema_glob: str = None, schema_url: str = None
) -> GraphQLSchema:
    if schema_dsl:
        return build_ast_schema(parse(schema_dsl))
    if schema_glob:
        schema_glob = glob(schema_glob, recursive=True)
        dsl_string = ""
        for file in schema_glob:
            with open(file, "r") as f:
                if file.endswith(".graphql"):
                    dsl_string += f.read()

        assert dsl_string, f"No schema found in glob {schema_glob}"
        return build_ast_schema(parse(dsl_string))

    raise NotImplementedError("Please provide either a dsl or glob")


class ValidationError(ContinuationLinkError):
    pass


class ValidatingLink(ContinuationLink):
    def __init__(
        self,
        schema_dsl: str = None,
        schema_glob: str = None,
        allow_introspection=True,
        introspect_on_connect=True,
    ) -> None:
        if schema_dsl or schema_glob:
            self.schema = schemify(schema_dsl, schema_glob)

        self.allow_introspection = allow_introspection
        self.introspect_on_connect = introspect_on_connect

    async def __aenter__(self) -> None:
        if not self.schema and self.introspect_on_connect:
            introspect_operation = opify(get_introspection_query())
            schema_result = await self.next.aquery(introspect_operation)
            self.schema = build_schema(schema_result.data)

    async def aload_schema(self, operation: Operation) -> None:
        if self.allow_introspection:
            introspect_operation = opify(get_introspection_query())
            introspect_operation.context = operation.context
            introspect_operation.extensions = operation.extensions

            schema_result = await self.next.aquery(introspect_operation)
            self.schema = build_schema(schema_result.data)

    def load_schema(self, operation: Operation) -> None:
        if self.allow_introspection:
            introspect_operation = opify(get_introspection_query())
            introspect_operation.context = operation.context
            introspect_operation.extensions = operation.extensions

            schema_result = self.next.query(introspect_operation)
            self.schema = build_schema(schema_result.data)

    def validate(self, operation: Operation):
        errors = validate(self.schema, operation.document_node)

        if len(errors) > 0:
            raise ValidationError(
                f"{operation} does not comply with the schema!\n Errors: \n\n"
                + "\n".join([e.message for e in errors])
            )

    async def aquery(self, operation: Operation, **kwargs) -> GraphQLResult:
        if not self.schema:
            await self.aload_schema(operation)

        self.validate(operation)
        return await self.next.aquery(operation, **kwargs)

    async def asubscribe(
        self, operation: Operation, **kwargs
    ) -> AsyncIterator[GraphQLResult]:
        if not self.schema:
            await self.aload_schema(operation)

        self.validate(operation)
        async for result in self.next.asubscribe(operation, **kwargs):
            yield result

    def query(self, operation: Operation, **kwargs) -> GraphQLResult:
        if not self.schema:
            self.load_schema(operation)

        self.validate(operation)
        return self.next.query(operation, **kwargs)

    def subscribe(self, operation: Operation, **kwargs) -> AsyncIterator[GraphQLResult]:
        if not self.schema:
            self.load_schema(operation)

        self.validate(operation)
        return self.next.subscribe(operation, **kwargs)
