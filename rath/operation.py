from typing import Optional, Dict, Any
from graphql.language import OperationDefinitionNode, parse
from graphql import (
    DocumentNode,
    get_operation_ast,
    parse,
)
from pydantic import BaseModel, Field


class Context(BaseModel):
    headers: Optional[Dict[str, str]] = Field(default_factory=dict)
    files: Optional[Dict[str, Any]] = Field(default_factory=dict)
    kwargs: Optional[Dict[str, Any]] = Field(default_factory=dict)


class Extensions(BaseModel):
    pollInterval: Optional[int] = None
    maxPolls: Optional[int] = None


class Operation(BaseModel):
    document_node: DocumentNode
    node: OperationDefinitionNode
    document: str
    variables: Dict[str, Any]
    operation_name: Optional[str]
    extensions: Extensions
    context: Context

    class Config:
        arbitrary_types_allowed = True


class GraphQLResult(BaseModel):
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
