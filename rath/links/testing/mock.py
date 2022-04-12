import asyncio
from typing import AsyncIterator, Awaitable, Callable, Dict

from pydantic import Field, validator
from rath.links.base import AsyncTerminatingLink
from rath.operation import GraphQLResult, Operation
from graphql import FieldNode, OperationType


def target_from_node(node: FieldNode) -> str:
    return (
        node.alias.value if hasattr(node, "alias") and node.alias else node.name.value
    )


class AsyncMockResolver:
    def to_dict(self):
        methods = [
            i for i in self.__class__.__dict__.keys() if i.startswith("resolve_")
        ]
        return {i[8:]: getattr(self, i) for i in methods}


class AsyncMockLink(AsyncTerminatingLink):
    query_resolver: Dict[str, Callable[[Operation], Awaitable[Dict]]] = Field(
        default_factory=dict, exclude=True
    )
    mutation_resolver: Dict[str, Callable[[Operation], Awaitable[Dict]]] = Field(
        default_factory=dict, exclude=True
    )
    subscription_resolver: Dict[str, Callable[[Operation], Awaitable[Dict]]] = Field(
        default_factory=dict, exclude=True
    )
    resolver: Dict[str, Callable[[Operation], Awaitable[Dict]]] = Field(
        default_factory=dict, exclude=True
    )

    @validator(
        "query_resolver",
        "mutation_resolver",
        "subscription_resolver",
        "resolver",
        pre=True,
    )
    @classmethod
    def coerce_resolver(cls, v):
        if isinstance(v, AsyncMockResolver):
            return v.to_dict()
        return v

    async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:

        if operation.node.operation == OperationType.QUERY:
            futures = []

            for op in operation.node.selection_set.selections:
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
                }
            )

        if operation.node.operation == OperationType.MUTATION:
            futures = []

            for op in operation.node.selection_set.selections:
                if op.name.value in self.mutation_resolver:
                    futures.append(self.mutation_resolver[op.name.value](operation))
                elif op.name.value in self.resolver:
                    futures.append(self.resolver[op.name.value](operation))
                else:
                    raise NotImplementedError(
                        f"Mocked Resolver for Query '{op.name.value}' not in resolvers: {self.mutation_resolver}, {self.resolver}  for AsyncMockLink"
                    )

            resolved = await asyncio.gather(*futures)
            yield GraphQLResult(
                data={
                    target_from_node(op): resolved[i]
                    for i, op in enumerate(operation.node.selection_set.selections)
                }
            )

        if operation.node.operation == OperationType.SUBSCRIPTION:
            futures = []
            assert (
                len(operation.node.selection_set.selections) == 1
            ), "Only one Subscription at a time possible"

            op = operation.node.selection_set.selections[0]
            if op.name.value in self.subscription_resolver:
                iterator = self.subscription_resolver[op.name.value](operation)
            elif op.name.value in self.resolver:
                iterator = self.resolver[op.name.value](operation)
            else:
                raise NotImplementedError(
                    f"Mocked Resolver for Query '{op.name.value}' not in resolvers: {self.subscription_resolver}, {self.resolver}  for AsyncMockLink"
                )

            async for event in iterator:
                yield GraphQLResult(data={target_from_node(op): event})

        else:
            raise NotImplementedError("Only subscription are mocked")
