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
        self.link(self)

        if register:
            set_current_rath(self)

    async def asubscribe(self):
        pass

    async def aexecute(
        self,
        query: str,
        variables: Dict[str, Any] = None,
        headers: Dict[str, Any] = {},
        operation_name=None,
        **kwargs,
    ) -> GraphQLResult:

        op = opify(query, variables, headers, operation_name, **kwargs)

        return await self.link.aquery(
            op,
        )

    def execute(
        self,
        query: str,
        variables: Dict[str, Any] = None,
        headers: Dict[str, Any] = {},
        operation_name=None,
        **kwargs,
    ) -> GraphQLResult:
        op = opify(query, variables, headers, operation_name, **kwargs)

        return self.link.query(
            op,
        )

    def subscribe(
        self,
        query: str,
        variables: Dict[str, Any] = None,
        headers: Dict[str, Any] = {},
        operation_name=None,
        **kwargs,
    ) -> Iterator[GraphQLResult]:

        op = opify(query, variables, headers, operation_name, **kwargs)
        for res in self.link.subscribe(op):
            yield res

    async def asubscribe(
        self,
        query: str,
        variables: Dict[str, Any] = None,
        headers: Dict[str, Any] = {},
        operation_name=None,
        **kwargs,
    ) -> AsyncIterator[GraphQLResult]:

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
