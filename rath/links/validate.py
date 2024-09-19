from typing import AsyncIterator, Optional, cast, Dict, Any, Type
from graphql import (
    GraphQLSchema,
    build_ast_schema,
    build_client_schema,
    get_introspection_query,
    validate,
    IntrospectionQuery,
)
from graphql.language.parser import parse
from pydantic import model_validator
from rath.links.base import ContinuationLink
from rath.links.errors import ContinuationLinkError
from rath.operation import GraphQLResult, Operation, opify
from glob import glob


def schemify(
    schema_dsl: Optional[str] = None, schema_glob: Optional[str] = None
) -> GraphQLSchema:
    """Schemify creates a GraphQLSchema from a schema dsl or a glob to a set of graphql files

    Parameters
    ----------
    schema_dsl : Optional[str], optional
        The schema_dsl to use, by default None
    schema_glob : Optional[str], optional
        A path/glaob to the schema files, by default None

    Returns
    -------
    GraphQLSchema
        The schema

    """

    if schema_dsl:
        return build_ast_schema(parse(schema_dsl))
    if schema_glob:
        files = glob(schema_glob, recursive=True)
        dsl_string = ""
        for file in files:
            with open(file, "r") as f:
                if file.endswith(".graphql"):
                    dsl_string += f.read()

        assert dsl_string, f"No schema found in glob {schema_glob}"
        return build_ast_schema(parse(dsl_string))

    raise NotImplementedError("Please provide either a dsl or glob")


class ValidationError(ContinuationLinkError):
    """ValidationError is raised when a validation error occurs"""

    pass


class ValidatingLink(ContinuationLink):
    """ValidatingLink validates the operation againt as schema before passing it on to the next link.

    The schema can be provided as a dsl string, or as a glob to a set of graphql files.
    If the schema is not provided, the link will introspect the server to get the schema if allow_introspection is set to True.


    """

    schema_dsl: Optional[str] = None
    """ The schema (as a string) to validate against. If not provided, the link will introspect the server to get the schema if allow_introspection is set to True."""
    schema_glob: Optional[str] = None
    """ The glob to a set of graphql files to validate against. If not provided, the link will introspect the server to get the schema if allow_introspection is set to True."""
    allow_introspection: bool = False
    """ If set to True, the link will introspect the server to get the schema if it is not provided."""

    graphql_schema: Optional[GraphQLSchema] = None
    """ The schema to validate against. If not provided, the link will introspect the server to get the schema if allow_introspection is set to True."""

    @model_validator(mode="after")
    @classmethod
    def check_schema_dsl_or_schema_glob(cls: Type["ValidatingLink"], self: "ValidatingLink", *info) -> Dict[str, Any]:  # type: ignore
        """Validates and checks that either a schema_dsl or schema_glob is provided, or that allow_introspection is set to True"""
        if not self.schema_dsl and not self.schema_glob:
            if not self.allow_introspection:
                raise ValueError(
                    "Please provide either a schema_dsl or schema_glob or allow introspection"
                )

        else:
            self.graphql_schema = schemify(
                schema_dsl=self.schema_dsl,
                schema_glob=self.schema_glob,
            )

        return self

    async def introspect(self, starting_operation: Operation) -> GraphQLSchema:  # type: ignore
        """Introspects the server to get the schema

        Parameters
        ----------
        starting_operation : Operation
            The operation to use for introspection (can be used to set headers, etc.)

        Returns
        -------
        GraphQLSchema
            The introspected schema
        """
        if not self.next:
            raise ContinuationLinkError("No next link set")

        introspect_operation = opify(get_introspection_query())
        introspect_operation.context = starting_operation.context
        introspect_operation.extensions = starting_operation.extensions

        async for result in self.next.aexecute(introspect_operation):
            return build_client_schema(cast(IntrospectionQuery, result.data))

    async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
        """Executes an operation against the link

        This link will validate the operation and then forward it to the next link,
        the next link will then execute the operation.

        Parameters
        ----------
        operation : Operation
            The operation to execute

        Yields
        ------
        GraphQLResult
            The result of the operation
        """
        if not self.next:
            raise ContinuationLinkError("No next link set")

        if not self.graphql_schema:
            assert self.allow_introspection, "Introspection is not allowed"
            self.graphql_schema = await self.introspect(operation)

        errors = validate(self.graphql_schema, operation.document_node)
        if len(errors) > 0:
            raise ValidationError(
                f"{operation} does not comply with the schema!\n Errors: \n\n"
                + "\n".join([e.message for e in errors])
            )

        async for result in self.next.aexecute(operation):
            yield result
