from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from graphql.language import OperationDefinitionNode, parse


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
    operation_name: str = None,
    **kwargs,
) -> Operation:

    document = parse(query)

    op = [o for o in document.definitions if isinstance(o, OperationDefinitionNode)][0]

    return Operation(
        node=op,
        document=query,
        variables=variables or {},
        operation_name=operation_name,
        extensions={},
        context=Context(headers=headers, kwargs=kwargs),
    )
