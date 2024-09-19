from typing import Optional, Dict, Any, Union
from graphql.language import OperationDefinitionNode, print_ast
from graphql import (
    DocumentNode,
    get_operation_ast,
    parse,
)
from pydantic import BaseModel, ConfigDict, Field
import uuid


class Context(BaseModel):
    """Context provides a way to pass arbitrary data to resolvers on the context"""

    headers: Dict[str, str] = Field(default_factory=dict)
    files: Dict[str, Any] = Field(default_factory=dict)
    initial_payload: Dict[str, Any] = Field(default_factory=dict)
    kwargs: Dict[str, Any] = Field(default_factory=dict)


class Extensions(BaseModel):
    """Extensions is a map of additional metadata that can be used by the links in the chain"""

    pollInterval: Optional[int] = None
    maxPolls: Optional[int] = None


class Operation(BaseModel):
    """A GraphQL operation.

    An Operation is a GraphQL operation that can be executed by a GraphQL client.
    It is a combination of a query, variables, and headers, as well as a context
    that can be used to pass additional information to the link chain and
    extensions that can be used to pass additional information to the server.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_node: DocumentNode
    node: OperationDefinitionNode
    document: str
    variables: Dict[str, Any]
    operation_name: Optional[str]
    extensions: Extensions
    context: Context


class GraphQLResult(BaseModel):
    """GraphQLResult is the result of a GraphQL operation."""

    data: Dict[str, Any]


class GraphQLException(Exception):
    """GraphQLException is the base exception for all GraphQL errors."""

    pass


class SubscriptionDisconnect(GraphQLException):
    """SubscriptionDisconnect is raised when a subscription is disconnected."""

    pass


def opify(
    query: Union[str, DocumentNode],
    variables: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, Any]] = None,
    operation_name: Optional[str] = None,
    **kwargs,
) -> Operation:
    """Opify takes a query, variables, and headers and returns an Operation.

    Operations are the main way to interact with the GraphQL client, they are
    used to execute queries, mutations, and subscriptions, and can carry additional
    information in their context and extensions.

    Parameters
    ----------
    query : Union[str, DocumentNode]
        The query to execute
    variables : Optional[Dict[str, Any]], optional
        The variables to use, by default None
    headers : Optional[Dict[str, Any]], optional
        The headers to use, by default None
    operation_name : Optional[str], optional
        The operation name to use, by default None

    Returns
    -------
    Operation
        The operation that can be executed
    """

    document = parse(query) if isinstance(query, str) else query
    op = get_operation_ast(document, operation_name)
    assert op, f"No operation named {operation_name}"
    return Operation(
        node=op,
        document=print_ast(document),
        document_node=document,
        variables=variables or {},
        operation_name=operation_name,
        extensions=Extensions(),
        context=Context(headers=headers or {}, kwargs=kwargs),
    )
