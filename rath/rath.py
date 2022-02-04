from http.client import NotConnected
from koil import koil
from rath.errors import NotConnectedError
from rath.links.base import TerminatingLink
import asyncio
from typing import Dict, Any, Optional, List, Union, Callable, Awaitable
from rath.operation import GraphQLResult, opify
from contextvars import ContextVar


class Rath:
    def __init__(
        self,
        link: TerminatingLink,
        register=False,
        autoconnect=True,
    ) -> None:
        self.link = link
        self.autoconnect = autoconnect
        self.link(self)
        self.connected = False

        if register:
            set_current_rath(self)

    async def aconnect(self):
        await self.link.aconnect()
        self.connected = True

    def connect(self):
        return koil(self.aconnect())

    async def asubscribe(self):
        pass

    async def aexecute(
        self,
        query: str,
        variables: Dict[str, Any] = None,
        headers: Dict[str, Any] = {},
        operation_name="",
        **kwargs,
    ) -> GraphQLResult:

        if not self.connected:
            if not self.autoconnect:
                raise NotConnectedError(
                    "Rath is not connected and autoconnect is set to false. Please connect first or set autoconnect to true."
                )

            await self.aconnect()

        op = opify(query, variables, headers, operation_name, **kwargs)

        for parser in self.parsers:
            op = await parser.aparse(op)

        return await self.link.aquery(
            op,
        )

    def execute(
        self,
        query: str,
        variables: Dict[str, Any] = None,
        headers: Dict[str, Any] = {},
        operation_name="",
        **kwargs,
    ) -> GraphQLResult:
        op = opify(query, variables, headers, operation_name, **kwargs)

        if not self.connected:
            if not self.autoconnect:
                raise NotConnectedError(
                    "Rath is not connected and autoconnect is set to false. Please connect first or set autoconnect to true."
                )
            koil(self.aconnect())

        return self.link.query(
            op,
        )

    def subscribe(
        self,
        query: str,
        variables: Dict[str, Any] = None,
        headers: Dict[str, Any] = {},
        operation_name="",
        **kwargs,
    ) -> GraphQLResult:

        op = opify(query, variables, headers, operation_name, **kwargs)
        for res in self.link.subscribe(op):
            yield res

    async def asubscribe(
        self,
        query: str,
        variables: Dict[str, Any] = None,
        headers: Dict[str, Any] = {},
        operation_name="",
        **kwargs,
    ) -> GraphQLResult:
        op = opify(query, variables, headers, operation_name, **kwargs)
        async for res in self.link.asubscribe(op):
            yield res


CURRENT_RATH = None


def get_current_rath(**kwargs):
    global CURRENT_RATH
    assert CURRENT_RATH is not None, "No current rath set"
    return CURRENT_RATH


def set_current_rath(rath):
    global CURRENT_RATH
    CURRENT_RATH = rath
