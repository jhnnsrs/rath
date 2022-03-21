import asyncio
from koil.composition import KoiledModel
from rath.errors import NotConnectedError
from rath.links.base import TerminatingLink
from typing import (
    AsyncIterator,
    Dict,
    Any,
    Iterator,
    Optional,
)
from rath.operation import GraphQLResult, opify
from contextvars import ContextVar


current_rath = ContextVar("current_rath")


class Rath(KoiledModel):
    link: Optional[TerminatingLink] = None
    set_context: bool = True

    _connected = False

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
        if self.set_context:
            current_rath.set(self)
        await self.link.__aenter__()
        self._connected = True
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.link.__aexit__(*args, **kwargs)
        self._connected = False
        if self.set_context:
            current_rath.set(None)

    class Config:
        underscore_attrs_are_private = True
