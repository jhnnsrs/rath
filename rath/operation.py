from dataclasses import dataclass, field
from glob import glob
from typing import Optional, Dict, Any
from graphql.language import OperationDefinitionNode, parse
from graphql import (
    DocumentNode,
    GraphQLSchema,
    get_introspection_query,
    get_operation_ast,
    parse,
    build_ast_schema,
)


@dataclass
class Context:
    headers: Optional[Dict[str, str]] = field(default_factory=dict)
    files: Optional[Dict[str, Any]] = field(default_factory=dict)
    kwargs: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass
class Extensions:
    pollInterval: Optional[int] = None
    maxPolls: Optional[int] = None


@dataclass
class Operation:
    document_node: DocumentNode
    node: OperationDefinitionNode
    document: str
    variables: Dict[str, Any]
    operation_name: str
    extensions: Extensions
    context: Context


@dataclass
class GraphQLResult:
    data: Dict[str, Any]


class GraphQLException(Exception):
    pass


def opify(
    query: str,
    variables: Dict[str, Any] = None,
    headers: Dict[str, Any] = {},
    operation_name: Optional[str] = None,
    **kwargs,
) -> Operation:

    document = parse(query)
    print(operation_name)
    op = get_operation_ast(document, operation_name)
    assert op, f"No operation named {operation_name}"
    return Operation(
        node=op,
        document=query,
        document_node=document,
        variables=variables or {},
        operation_name=operation_name,
        extensions={},
        context=Context(headers=headers, kwargs=kwargs),
    )


def schemify(schema_dsl: str = None, schema_glob: str = None) -> GraphQLSchema:
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
