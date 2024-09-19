import asyncio
from typing import AsyncIterator, Awaitable, Callable, Dict, Type, Any

from pydantic import Field, field_validator
from rath.links.base import AsyncTerminatingLink
from rath.operation import GraphQLResult, Operation
from graphql import FieldNode, OperationType


def target_from_node(node: FieldNode) -> str:
    """Extract the target aka. the aliased name from a FieldNode."""
    return (
        node.alias.value if hasattr(node, "alias") and node.alias else node.name.value
    )


class AsyncMockResolver:
    """A Mock Resolver

    This is a mock resolver that can be used to mock a GraphQL server.
    Every attribute that starts with resolve_ will be used as a resolver
    for the corresponding field.
    """

    def to_dict(self) -> Dict[str, Callable[[Operation], Awaitable[Dict]]]:
        """Convert the Mock Resolver to a dict of resolvers

        Returns
        -------
        Dict[str, Callable[[Operation], Awaitable[Dict]]]
            The dict of resolvers
        """
        methods = [
            i for i in self.__class__.__dict__.keys() if i.startswith("resolve_")
        ]
        return {i[8:]: getattr(self, i) for i in methods}


ResolverDict = Dict[str, Callable[[Operation], Awaitable[Dict]]]


class AsyncMockLink(AsyncTerminatingLink):
    """A Mocklink

    This is a mocklink that can be used to mock a GraphQL server.
    You need to pass resolvers to the constructor.
    """

    query_resolver: Dict[str, Callable[[Operation], Awaitable[Dict]]] = Field(
        default_factory=dict, exclude=True
    )
    mutation_resolver: Dict[str, Callable[[Operation], Awaitable[Dict]]] = Field(
        default_factory=dict, exclude=True
    )
    subscription_resolver: Dict[str, Callable[[Operation], AsyncIterator[Dict]]] = (
        Field(default_factory=dict, exclude=True)
    )
    resolver: ResolverDict = Field(default_factory=dict, exclude=True)

    @field_validator(
        "query_resolver",
        "mutation_resolver",
        "subscription_resolver",
        "resolver",
        mode="before",
    )
    @classmethod
    def coerce_resolver(cls: Type["AsyncMockLink"], v: Any) -> ResolverDict:
        """A validator that coerces AsyncMockResolver to a dict of resolvers"""
        if isinstance(v, AsyncMockResolver):
            return v.to_dict()
        return v

    async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
        """Executes an operation against the link

        Parameters
        ----------
        operation : Operation
            The operation to execute

        Yields
        ------
        GraphQLResult
            The result of the operation
        """

        if operation.node.operation == OperationType.QUERY:
            futures = []

            for op in operation.node.selection_set.selections:
                if isinstance(op, FieldNode):
                    if op.name.value in self.query_resolver:
                        futures.append(self.query_resolver[op.name.value](operation))
                    elif op.name.value in self.resolver:
                        futures.append(self.resolver[op.name.value](operation))
                    else:
                        raise NotImplementedError(
                            f"Mocked Resolver for Query '{op.name.value}' not in resolvers: {self.query_resolver}, {self.resolver}  for AsyncMockLink"
                        )

            resolved = await asyncio.gather(*futures)
            yield GraphQLResult(
                data={
                    target_from_node(op): resolved[i]
                    for i, op in enumerate(operation.node.selection_set.selections)
                    if isinstance(op, FieldNode)
                }
            )

        if operation.node.operation == OperationType.MUTATION:
            futures = []

            for op in operation.node.selection_set.selections:
                if isinstance(op, FieldNode):
                    if op.name.value in self.mutation_resolver:
                        futures.append(self.mutation_resolver[op.name.value](operation))
                    elif op.name.value in self.resolver:
                        futures.append(self.resolver[op.name.value](operation))
                    else:
                        raise NotImplementedError(
                            f"Mocked Resolver for Query '{op.name.value}' not in resolvers:"
                            f"{self.mutation_resolver}, {self.resolver}  for AsyncMockLink"
                        )

            resolved = await asyncio.gather(*futures)
            yield GraphQLResult(
                data={
                    target_from_node(op): resolved[i]
                    for i, op in enumerate(operation.node.selection_set.selections)
                    if isinstance(op, FieldNode)
                }
            )

        if operation.node.operation == OperationType.SUBSCRIPTION:
            futures = []
            assert (
                len(operation.node.selection_set.selections) == 1
            ), "Only one Subscription at a time possible"

            op = operation.node.selection_set.selections[0]
            if isinstance(op, FieldNode):
                if op.name.value in self.subscription_resolver:
                    iterator = self.subscription_resolver[op.name.value](operation)

                    async for event in iterator:
                        if isinstance(op, FieldNode):
                            yield GraphQLResult(data={target_from_node(op): event})
                else:
                    raise NotImplementedError(
                        f"Mocked Resolver for Query '{op.name.value}' not in resolvers"
                        f": {self.subscription_resolver}, {self.resolver}  for AsyncMockLink"
                    )

            async for event in iterator:
                if isinstance(op, FieldNode):
                    yield GraphQLResult(data={target_from_node(op): event})

        else:
            raise NotImplementedError("Only subscription are mocked")
