from koil.composition import KoiledModel
from rath.errors import NotConnectedError, NotEnteredError
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
from koil import unkoil_gen, unkoil


current_rath = ContextVar("current_rath")


class Rath(KoiledModel):
    link: Optional[TerminatingLink] = None
    set_context: bool = True

    _connected = False
    _entered = False
    auto_connect = True
    connect_on_enter: bool = False

    async def aconnect(self):
        if not self._entered:
            raise NotEnteredError(
                "You need to use enter `async with Rath(...) as rath`"
            )
        await self.link.aconnect()
        self._connected = True

    async def adisconnect(self):
        await self.link.adisconnect()
        self._connected = False

    async def aquery(
        self,
        query: str,
        variables: Dict[str, Any] = None,
        headers: Dict[str, Any] = {},
        operation_name=None,
        **kwargs,
    ) -> GraphQLResult:
        if not self._connected:
            if not self.auto_connect:
                raise NotConnectedError(
                    "Rath is not connected. Please use `async with Rath(..., auto_connect=True) as rath` or use `await rath.aconnect() before`"
                )
            await self.aconnect()

        op = opify(query, variables, headers, operation_name, **kwargs)

        async for data in self.link.aexecute(op):
            return data

    def query(
        self,
        query: str,
        variables: Dict[str, Any] = None,
        headers: Dict[str, Any] = {},
        operation_name=None,
        **kwargs,
    ) -> GraphQLResult:
        return unkoil(self.aquery, query, variables, headers, operation_name, **kwargs)

    def subscribe(
        self,
        query: str,
        variables: Dict[str, Any] = None,
        headers: Dict[str, Any] = {},
        operation_name=None,
        **kwargs,
    ) -> Iterator[GraphQLResult]:
        return unkoil_gen(
            self.asubscribe, query, variables, headers, operation_name, **kwargs
        )

    async def asubscribe(
        self,
        query: str,
        variables: Dict[str, Any] = None,
        headers: Dict[str, Any] = {},
        operation_name=None,
        **kwargs,
    ) -> AsyncIterator[GraphQLResult]:
        if not self._connected:
            if not self.auto_connect:
                raise NotConnectedError(
                    "Rath is not connected. Please use `async with Rath(..., auto_connect=True) as rath` or use `await rath.aconnect() before`"
                )
            await self.aconnect()

        op = opify(query, variables, headers, operation_name, **kwargs)
        async for data in self.link.aexecute(op):
            yield data

    async def __aenter__(self):
        self._entered = True
        if self.set_context:
            current_rath.set(self)
        await self.link.__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        if self._connected:
            await self.adisconnect()

        await self.link.__aexit__(*args, **kwargs)
        self._entered = False
        if self.set_context:
            current_rath.set(None)

    class Config:
        underscore_attrs_are_private = True
