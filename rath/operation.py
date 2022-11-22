from typing import Optional, Dict, Any, Union
from graphql.language import OperationDefinitionNode, parse
from graphql import (
    DocumentNode,
    get_operation_ast,
    parse,
)
from pydantic import BaseModel, Field
import uuid


class Context(BaseModel):
    """Context provides a way to pass arbitrary data to resolvers on the context"""
    headers: Optional[Dict[str, str]] = Field(default_factory=dict)
    files: Optional[Dict[str, Any]] = Field(default_factory=dict)
    kwargs: Optional[Dict[str, Any]] = Field(default_factory=dict)


class Extensions(BaseModel):
    """ Extensions is a map of additional metadata that can be used by the links in the chain"""
    pollInterval: Optional[int] = None
    maxPolls: Optional[int] = None


class Operation(BaseModel):
    """A GraphQL operation.
    
    An Operation is a GraphQL operation that can be executed by a GraphQL client.
    It is a combination of a query, variables, and headers, as well as a context
    that can be used to pass additional information to the link chain and
    extensions that can be used to pass additional information to the server.
    """


    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
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
    """GraphQLResult is the result of a GraphQL operation."""
    data: Dict[str, Any]


class GraphQLException(Exception):
    """GraphQLException is the base exception for all GraphQL errors."""
    pass


class SubscriptionDisconnect(GraphQLException):
    pass


def opify(
    query: Union[str, DocumentNode],
    variables: Dict[str, Any] = None,
    headers: Dict[str, Any] = None,
    operation_name: Optional[str] = None,
    **kwargs,
) -> Operation:
    """Opify takes a query, variables, and headers and returns an Operation.

    Args:
        query (Union[str, DocumentNode]): The query string or the DocumentNode.
        variables (Dict[str, Any], optional): The variables. Defaults to None.
        headers (Dict[str, Any], optional): Additional headers. Defaults to None.
        operation_name (Optional[str], optional): The operation_name to be exceuted. Defaults to None.

    Returns:
        Operation: A GraphQL operation
    """

    document = parse(query) if query and isinstance(query, str) else query
    op = get_operation_ast(document, operation_name)
    assert op, f"No operation named {operation_name}"
    return Operation(
        node=op,
        document=query,
        document_node=document,
        variables=variables or {},
        operation_name=operation_name,
        extensions={},
        context=Context(headers=headers or {}, kwargs=kwargs),
    )
