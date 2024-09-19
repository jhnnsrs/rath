import asyncio
from typing import AsyncIterator, Awaitable, Callable, Dict, Optional, Type, Any

from pydantic import Field, field_validator
from rath.links.base import AsyncTerminatingLink
from rath.links.testing.mock import AsyncMockResolver
from rath.operation import GraphQLResult, Operation
from graphql import FieldNode, OperationType
import uuid
from rath.links.errors import TerminatingLinkError


def target_from_node(node: FieldNode) -> str:
    """Extract the target aka. the aliased name from a FieldNode.

    Args:
        node (FieldNode): A GraphQL FieldNode.

    Returns:
        str: The target
    """
    return (
        node.alias.value if hasattr(node, "alias") and node.alias else node.name.value
    )


class ConfigurationError(TerminatingLinkError):
    """A Configuration Error"""


class AsyncStatefulMockLink(AsyncTerminatingLink):
    """A Stateful Mocklink

    This is a mocklink that can be used to mock a GraphQL server.
    You need to pass resolvers to the constructor.

    In addition to AsyncMockLink this class also supports Subscription,
    and has internal state that needs to be handled.

    """

    timeout: float = 2

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

    _connection_lock: Optional[asyncio.Lock] = None
    _connected: bool = False
    _futures: Optional[Dict[str, asyncio.Future]] = None
    _inqueue: Optional[asyncio.Queue] = None
    _connection_task: Optional[asyncio.Task] = None

    @field_validator(
        "query_resolver",
        "mutation_resolver",
        "subscription_resolver",
        "resolver",
        mode="before",
    )
    @classmethod
    def coerce_resolver(cls: Type["AsyncStatefulMockLink"], v: Any) -> Dict[str, Any]:
        """Coerce the resolver to a dict if it is a AsyncMockResolver"""
        if isinstance(v, AsyncMockResolver):
            return v.to_dict()
        return v

    async def __aenter__(self) -> None:
        """Aenter the link and set up the internal state"""
        self._connection_lock = asyncio.Lock()
        return await super().__aenter__()

    async def aconnect(self, operation: Operation) -> None:
        """Connect the link and set up the internal state"""
        self._futures = {}
        self._inqueue = asyncio.Queue()
        _connection_future = asyncio.Future()  # type: ignore
        self._connection_task = asyncio.create_task(self.resolving(_connection_future))
        await _connection_future

    async def adisconnect(self) -> None:
        """Disconnect the link and clean up the internal state"""
        if self._connection_task:
            self._connection_task.cancel()
            self._connected = False

            try:
                await self._connection_task
            except asyncio.CancelledError:
                pass

    async def __aexit__(self, *args, **kwargs) -> None:
        """Aexit the link and clean up the internal state"""
        await self.adisconnect()

    async def resolving(self, connection_future: asyncio.Future) -> None:
        """A coroutine that resolves the incoming operations in
        an inifite Loop

        Raises:
            NotImplementedError: If the operation is not supported (aka not implemented)
        """
        connection_future.set_result(True)
        while True:
            if self._inqueue is None:
                raise ConfigurationError(
                    "You need to call aconnect before you can resolve operations"
                )

            operation, id = await self._inqueue.get()

            resolve_futures = []

            try:
                if operation.node.operation == OperationType.QUERY:
                    for op in operation.node.selection_set.selections:
                        if op.name.value in self.query_resolver:
                            resolve_futures.append(
                                self.query_resolver[op.name.value](operation)
                            )
                        elif op.name.value in self.resolver:
                            resolve_futures.append(
                                self.resolver[op.name.value](operation)
                            )
                        else:
                            raise NotImplementedError(
                                f"Mocked Resolver for Query '{op.name.value}' not in resolvers"
                                f": {self.query_resolver}, {self.resolver}  for AsyncMockLink"
                            )

                if operation.node.operation == OperationType.MUTATION:
                    for op in operation.node.selection_set.selections:
                        if op.name.value in self.mutation_resolver:
                            resolve_futures.append(
                                self.mutation_resolver[op.name.value](operation)
                            )
                        elif op.name.value in self.resolver:
                            resolve_futures.append(
                                self.resolver[op.name.value](operation)
                            )
                        else:
                            raise NotImplementedError(
                                f"Mocked Resolver for Query '{op.name.value}' not in resolvers:"
                                f"{self.mutation_resolver}, {self.resolver}  for AsyncMockLink"
                            )
                resolved = await asyncio.gather(*resolve_futures)

                if not self._futures:
                    self._futures = {}

                self._futures[id].set_result(
                    GraphQLResult(
                        data={
                            target_from_node(op): resolved[i]
                            for i, op in enumerate(
                                operation.node.selection_set.selections
                            )
                        }
                    )
                )
            except AttributeError as t:
                raise ConfigurationError(f"No resolver for operation {op}") from t

            except Exception as e:
                if not self._futures:
                    self._futures = {}

                self._futures[id].set_exception(e)

            self._inqueue.task_done()

    async def submit(self, o: Operation, id: str) -> None:
        """Submit an operation to the resolver"""
        if self._inqueue is None:
            raise ConfigurationError(
                "You need to call aconnect before you can submit operations"
            )
        await self._inqueue.put((o, id))

    async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
        """Executes an operation against the link

        This link will send the operation to the correct resolver and return the result.

        Parameters
        ----------
        operation : Operation
            The operation to execute

        Yields
        ------
        GraphQLResult
            The result of the operation
        """
        if self._connection_lock is None:
            raise ConfigurationError(
                "You need to call __aenter__ before you can execute operations"
            )

        if not self._futures:
            self._futures = {}

        async with self._connection_lock:
            if not self._connected:
                await self.aconnect(operation)

        if (
            operation.node.operation == OperationType.QUERY
            or operation.node.operation == OperationType.MUTATION
        ):
            uniqueid = str(uuid.uuid4())
            self._futures[uniqueid] = asyncio.Future()
            await self.submit(operation, uniqueid)
            yield await asyncio.wait_for(self._futures[uniqueid], timeout=self.timeout)

        if operation.node.operation == OperationType.SUBSCRIPTION:
            assert (
                len(operation.node.selection_set.selections) == 1
            ), "Only one Subscription at a time possible"

            op = operation.node.selection_set.selections[0]
            if not isinstance(op, FieldNode):  # pragma: no cover
                raise NotImplementedError("Only FieldNode are supported")

            if op.name.value in self.subscription_resolver:
                iterator = self.subscription_resolver[op.name.value](operation)
            elif op.name.value in self.resolver:
                iterator = self.resolver[op.name.value](operation)
            else:
                raise NotImplementedError(
                    f"Mocked Resolver for Query '{op.name.value}' not in resolvers: {self.subscription_resolver}, {self.resolver}  for AsyncMockLink"
                )

            async for event in iterator:  # type: ignore
                yield GraphQLResult(data={target_from_node(op): event})

        else:
            raise NotImplementedError("Only subscription are mocked")
