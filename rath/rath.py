import asyncio
from koil.decorators import koilable
from rath.errors import NotConnectedError
from rath.links.base import TerminatingLink
from typing import (
    AsyncIterator,
    Dict,
    Any,
    Iterator,
)
from rath.operation import GraphQLResult, opify
from contextvars import ContextVar


current_rath = ContextVar("current_rath")


@koilable(add_connectors=True)
class Rath:
    def __init__(
        self,
        link: TerminatingLink,
        set_context=True,
    ) -> None:
        """Initialize a Rath client

        Rath takes a instance of TerminatingLink and creates an interface around it
        to enable easy usage of the GraphQL API.

        Args:
            link (TerminatingLink): A terminating link or a composed link.
        """
        self.link = link
        self.set_context = set_context
        self._connected = False

    async def aexecute(
        self,
        query: str,
        variables: Dict[str, Any] = None,
        headers: Dict[str, Any] = {},
        operation_name=None,
        timeout=None,
        **kwargs,
    ) -> GraphQLResult:
        if not self._connected:
            raise NotConnectedError(
                "Rath is not connected. Please use `async with Rath(...) as rath` or use `await rath.aconnect() before`"
            )
        op = opify(query, variables, headers, operation_name, **kwargs)

        if timeout:
            return await asyncio.wait_for(self.link.aquery(op), timeout)

        return await self.link.aquery(op, **kwargs)

    def execute(
        self,
        query: str,
        variables: Dict[str, Any] = None,
        headers: Dict[str, Any] = {},
        operation_name=None,
        **kwargs,
    ) -> GraphQLResult:
        if not self._connected:
            raise NotConnectedError(
                "Rath is not connected. Please use `with Rath(...) as rath` or use `rath.connect() before`"
            )
        op = opify(query, variables, headers, operation_name, **kwargs)
        return self.link.query(op, **kwargs)

    def subscribe(
        self,
        query: str,
        variables: Dict[str, Any] = None,
        headers: Dict[str, Any] = {},
        operation_name=None,
        **kwargs,
    ) -> Iterator[GraphQLResult]:
        if not self._connected:
            raise NotConnectedError(
                "Rath is not connected. Please use `with Rath(...) as rath` or use `rath.connect() before`"
            )
        op = opify(query, variables, headers, operation_name, **kwargs)
        return self.link.subscribe(op, **kwargs)

    async def asubscribe(
        self,
        query: str,
        variables: Dict[str, Any] = None,
        headers: Dict[str, Any] = {},
        operation_name=None,
        **kwargs,
    ) -> AsyncIterator[GraphQLResult]:
        if not self._connected:
            raise NotConnectedError(
                "Rath is not connected. Please use `async with Rath(...) as rath` or use `await rath.aconnect() before`"
            )
        op = opify(query, variables, headers, operation_name, **kwargs)
        async for res in self.link.asubscribe(op, **kwargs):
            yield res

    async def __aenter__(self):
        self.link(self)
        if self.set_context:
            current_rath.set(self)
        await self.link.__aenter__()
        self._connected = True
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.link.__aexit__(*args, **kwargs)
        self._connected = False
        self.link(None)
        if self.set_context:
            current_rath.set(None)

    def __enter__(self) -> "Rath":
        ...
