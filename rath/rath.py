from koil import koil
from rath.parsers.base import Parser
from rath.transports.base import Transport
import asyncio
from typing import Dict, Any, Optional, List, Union, Callable, Awaitable
from rath.operation import GraphQLResult, opify
from contextvars import ContextVar


class Rath:
    parsers: List[Parser]

    def __init__(
        self, parsers: List[Parser], transport: Transport, register=False
    ) -> None:
        self.parsers = [parser(self) for parser in parsers]  # initialized defered
        self.transport = transport(self)

        if register:
            set_current_rath(self)

    async def aconnect(self):
        await asyncio.gather(*[parser.aconnect() for parser in self.parsers])
        await self.transport.aconnect()

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

        op = opify(query, variables, headers, operation_name, **kwargs)

        for parser in self.parsers:
            op = await parser.aparse(op)

        return await self.transport.aquery(
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

        for parser in self.parsers:
            op = parser.parse(op)

        return koil(
            self.transport.aquery(
                op,
            )
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

        for link in self.links:
            op = link.parse(op)

        pass

    async def asubscribe(
        self,
        query: str,
        variables: Dict[str, Any] = None,
        headers: Dict[str, Any] = {},
        operation_name="",
        **kwargs,
    ) -> GraphQLResult:
        pass


CURRENT_RATH = None


def get_current_rath(**kwargs):
    global CURRENT_RATH
    assert CURRENT_RATH is not None, "No current rath set"
    return CURRENT_RATH


def set_current_rath(rath):
    global CURRENT_RATH
    CURRENT_RATH = rath
