import asyncio
from koil.decorators import koilable
from rath.links.base import TerminatingLink
from typing import (
    AsyncIterator,
    Dict,
    Any,
    Iterator,
    Optional,
    List,
    Union,
    Callable,
    Awaitable,
)
from rath.operation import GraphQLResult, opify
from contextvars import ContextVar


@koilable(add_connectors=True)
class Rath:
    def __init__(
        self,
        link: TerminatingLink,
        register=False,
        autoconnect=True,
    ) -> None:
        """Initialize a Rath client

        Rath takes a instance of TerminatingLink and creates an interface around it
        to enable easy usage of the GraphQL API.

        Args:
            link (TerminatingLink): A terminating link or a composed link.
            register (bool, optional): Register as a global rath (knowing the risks). Defaults to False.
            autoconnect (bool, optional): [description]. Defaults to True.
        """
        self.link = link
        self.autoconnect = autoconnect

    async def aexecute(
        self,
        query: str,
        variables: Dict[str, Any] = None,
        headers: Dict[str, Any] = {},
        operation_name=None,
        timeout=None,
        **kwargs,
    ) -> GraphQLResult:

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

        op = opify(query, variables, headers, operation_name, **kwargs)
        print("subscribe here")
        return self.link.subscribe(op, **kwargs)

    async def asubscribe(
        self,
        query: str,
        variables: Dict[str, Any] = None,
        headers: Dict[str, Any] = {},
        operation_name=None,
        **kwargs,
    ) -> AsyncIterator[GraphQLResult]:

        op = opify(query, variables, headers, operation_name, **kwargs)
        async for res in self.link.asubscribe(op, **kwargs):
            yield res

    async def __aenter__(self):
        self.link(self)
        await self.link.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.link.__aexit__(exc_type, exc_val, exc_tb)
