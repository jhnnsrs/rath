import asyncio
from typing import AsyncIterator, Union
from rath.links.base import AsyncTerminatingLink
from rath.operation import GraphQLResult, Operation
from graphql import FieldNode, GraphQLSchema, OperationType, validate
import uuid
from rath.links.errors import LinkNotConnectedError


def target_from_node(node: FieldNode) -> str:
    return (
        node.alias.value if hasattr(node, "alias") and node.alias else node.name.value
    )


class AsyncMockResolver:
    def __getitem__(self, key):
        return getattr(self, f"resolve_{key}")

    def __contains__(self, key):
        return hasattr(self, f"resolve_{key}")


class AsyncStatefulMockLink(AsyncTerminatingLink):
    def __init__(
        self,
        resolver: Union[AsyncMockResolver, dict] = {},
        query_resolver: Union[AsyncMockResolver, dict] = None,
        mutation_resolver: Union[AsyncMockResolver, dict] = None,
        subscription_resolver: Union[AsyncMockResolver, dict] = None,
        schema: GraphQLSchema = None,
    ) -> None:
        self.query_resolver = query_resolver or resolver
        self.mutation_resolver = mutation_resolver or resolver
        self.subscription_resolver = subscription_resolver or resolver
        self.schema = schema
        self.connected = False
        self.futures = {}

    async def __aenter__(self) -> None:
        self.connected = True
        self._inqueue = asyncio.Queue()
        self.connection_task = asyncio.create_task(self.resolving())

    async def __aexit__(self, *args, **kwargs) -> None:
        self.connected = False
        self.connection_task.cancel()

        try:
            await self.connection_task
        except asyncio.CancelledError:
            pass

    async def resolving(self):
        while True:
            operation, id = await self._inqueue.get()

            resolve_futures = []

            try:
                if operation.node.operation == OperationType.QUERY:

                    for op in operation.node.selection_set.selections:
                        assert (
                            op.name.value in self.query_resolver
                        ), f"Mocked Resolver for Query '{op.name.value}' not in resolver: {self.query_resolver}  for AsyncMockLink"

                        resolve_futures.append(
                            self.query_resolver[op.name.value](operation)
                        )

                if operation.node.operation == OperationType.MUTATION:

                    for op in operation.node.selection_set.selections:
                        assert (
                            op.name.value in self.mutation_resolver
                        ), f"Mocked Resolver for Mutation {op.name.value} not in resolver: {self.mutation_resolver} for AsyncMockLink"
                        resolve_futures.append(
                            self.mutation_resolver[op.name.value](operation)
                        )

                resolved = await asyncio.gather(*resolve_futures)
                self.futures[id].set_result(
                    GraphQLResult(
                        data={
                            target_from_node(op): resolved[i]
                            for i, op in enumerate(
                                operation.node.selection_set.selections
                            )
                        }
                    )
                )

            except Exception as e:
                self.futures[id].set_exception(e)

            self._inqueue.task_done()

    async def submit(self, o, id):
        await self._inqueue.put((o, id))

    async def aquery(self, operation: Operation) -> GraphQLResult:
        if self.connected == False:
            raise LinkNotConnectedError("AsyncMockLink is not connected")

        uniqueid = uuid.uuid4()
        self.futures[uniqueid] = asyncio.Future()
        await self.submit(operation, uniqueid)
        return await self.futures[uniqueid]

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
