import asyncio
from typing import AsyncIterator, Union
from rath.links.base import AsyncTerminatingLink
from rath.operation import GraphQLResult, Operation
from graphql import FieldNode, GraphQLSchema, OperationType, validate


def target_from_node(node: FieldNode) -> str:
    return (
        node.alias.value if hasattr(node, "alias") and node.alias else node.name.value
    )


class AsyncMockResolver:
    def __getitem__(self, key):
        return getattr(self, f"resolve_{key}")

    def __contains__(self, key):
        return hasattr(self, f"resolve_{key}")


class AsyncMockLink(AsyncTerminatingLink):
    def __init__(
        self,
        resolver: Union[AsyncMockResolver, dict] = {},
        query_resolver: Union[AsyncMockResolver, dict] = None,
        mutation_resolver: Union[AsyncMockResolver, dict] = None,
        subscription_resolver: Union[AsyncMockResolver, dict] = None,
    ) -> None:
        self.query_resolver = query_resolver or resolver
        self.mutation_resolver = mutation_resolver or resolver
        self.subscription_resolver = subscription_resolver or resolver

    async def aquery(self, operation: Operation) -> GraphQLResult:

        if operation.node.operation == OperationType.QUERY:
            futures = []

            for op in operation.node.selection_set.selections:
                assert (
                    op.name.value in self.query_resolver
                ), f"Mocked Resolver for Query '{op.name.value}' not in resolver: {self.query_resolver}  for AsyncMockLink"
                futures.append(self.query_resolver[op.name.value](operation))

            resolved = await asyncio.gather(*futures)
            return GraphQLResult(
                data={
                    target_from_node(op): resolved[i]
                    for i, op in enumerate(operation.node.selection_set.selections)
                }
            )

        if operation.node.operation == OperationType.MUTATION:
            futures = []

            for op in operation.node.selection_set.selections:
                assert (
                    op.name.value in self.mutation_resolver
                ), f"Mocked Resolver for Mutation {op.name.value} not in resolver: {self.mutation_resolver} for AsyncMockLink"
                futures.append(self.mutation_resolver[op.name.value](operation))

            resolved = await asyncio.gather(*futures)
            return GraphQLResult(
                data={
                    target_from_node(op): resolved[i]
                    for i, op in enumerate(operation.node.selection_set.selections)
                }
            )

    async def asubscribe(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
        if operation.node.operation == OperationType.SUBSCRIPTION:
            futures = []
            assert (
                len(operation.node.selection_set.selections) == 1
            ), "Only one Subscription at a time possible"

            op = operation.node.selection_set.selections[0]
            assert (
                op.name.value in self.subscription_resolver
            ), f"Mocked Resolver for Subscription {op.name.value} not in resolver: {self.subscription_resolver} for AsyncMockLink"

            async for event in self.subscription_resolver[op.name.value](operation):
                yield GraphQLResult(data={target_from_node(op): event})

        else:
            raise NotImplementedError("Only subscription are mocked")
