from koil.composition import KoiledModel
from pydantic import Field
from rath.errors import NotConnectedError, NotEnteredError
from rath.links.base import TerminatingLink
from typing import (
    AsyncIterator,
    Dict,
    Any,
    Iterator,
    Optional,
)
from typing import Union
from graphql import (
    DocumentNode,
)
from rath.operation import GraphQLResult, opify
from contextvars import ContextVar
from koil import unkoil_gen, unkoil


current_rath = ContextVar("current_rath")


class Rath(KoiledModel):
    """A Rath is a client for a GraphQL API.

    Links are used to define the transport logic of the Rath. A Rath can be
    connected to a GraphQL API using a terminating link. By composing links to
    form a chain, you can define the transport logic of the client.

    For example, a Rath can be connected to a GraphQL API over HTTP by
    composing an HTTP terminating link with a RetryLink. The RetryLink will
    retry failed requests, and the HTTP terminating link will send the
    requests over HTTP.

    Example:
        ```python
        from rath import Rath
        from rath.links.retriy import RetryLink
        from rathlinks.aiohttp import  AioHttpLink

        retry = RetryLink()
        http = AioHttpLink("https://graphql-pokemon.now.sh/graphql")

        rath = Rath(link=compose(retry, link))
        async with rath as rath:
            await rath.aquery(...)
        ```

    """




    link: Optional[TerminatingLink] = None
    """The terminating link used to send operations to the server. Can be a composed link chain."""

    _connected = False
    _entered = False
    _context_token = None
    auto_connect = True
    """If true, the Rath will automatically connect to the server when a query is executed."""
    connect_on_enter: bool = False
    """If true, the Rath will automatically connect to the server when entering the context manager."""

    async def aconnect(self):
        """Connect to the server.

        This method needs to be called within the context of a Rath instance,
        to always ensure that the Rath is disconnected when the context is
        exited.

        This method is called automatically when a query is executed if
        `auto_connect` is set to True. 

        Raises:
            NotEnteredError: Raises an error if the Rath is not entered.
        """
        if not self._entered:
            raise NotEnteredError(
                "You need to use enter `async with Rath(...) as rath`"
            )
        await self.link.aconnect()
        self._connected = True

    async def adisconnect(self):
        """Disconnect from the server."""
        await self.link.adisconnect()
        self._connected = False

    async def aquery(
        self,
        query: Union[str, DocumentNode],
        variables: Dict[str, Any] = None,
        headers: Dict[str, Any] = None,
        operation_name: str =None,
        **kwargs,
    ) -> GraphQLResult:
        """Query the GraphQL API.

        Takes a querystring, variables, and headers and returns the result.
        If provided, the operation_name will be used to identify which operation
        to execute.

        Args:
            query (str | DocumentNode): The query string or the DocumentNode.
            variables (Dict[str, Any], optional): The variables. Defaults to None.
            headers (Dict[str, Any], optional): Additional headers. Defaults to None.
            operation_name (str, optional): The operation_name to executed. Defaults to all.
            **kwargs: Additional arguments to pass to the link chain

        Raises:
            NotConnectedError: An error when the Rath is not connected and autoload is set to false

        Returns:
            GraphQLResult: The result of the query
        """


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
        query: Union[str, DocumentNode],
        variables: Dict[str, Any] = None,
        headers: Dict[str, Any] = None,
        operation_name: str =None,
        **kwargs,
    ) -> GraphQLResult:
        """Query the GraphQL API.

        Takes a querystring, variables, and headers and returns the result.
        If provided, the operation_name will be used to identify which operation
        to execute.

        Args:
            query (str | DocumentNode): The query string or the DocumentNode.
            variables (Dict[str, Any], optional): The variables. Defaults to None.
            headers (Dict[str, Any], optional): Additional headers. Defaults to None.
            operation_name (str, optional): The operation_name to executed. Defaults to all.
            **kwargs: Additional arguments to pass to the link chain

        Raises:
            NotConnectedError: An error when the Rath is not connected and autoload is set to false

        Returns:
            GraphQLResult: The result of the query
        """
        return unkoil(self.aquery, query, variables, headers, operation_name, **kwargs)

    def subscribe(
        self,
        query: str,
        variables: Dict[str, Any] = None,
        headers: Dict[str, Any] = None,
        operation_name: str =None,
        **kwargs,
    ) -> Iterator[GraphQLResult]:
        """Subscripe to a GraphQL API.

        Takes a querystring, variables, and headers and returns an async iterator
        that yields the results.

        Args:
            query (str | DocumentNode): The query string or the DocumentNode.
            variables (Dict[str, Any], optional): The variables. Defaults to None.
            headers (Dict[str, Any], optional): Additional headers. Defaults to None.
            operation_name (str, optional): The operation_name to executed. Defaults to all.
            **kwargs: Additional arguments to pass to the link chain

        Raises:
            NotConnectedError: An error when the Rath is not connected and autoload is set to false

        Yields:
            Iterator[GraphQLResult]: The result of the query as an async iterator
        """ 
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
        """Subscripe to a GraphQL API.

        Takes a querystring, variables, and headers and returns an async iterator
        that yields the results.

        Args:
            query (str | DocumentNode): The query string or the DocumentNode.
            variables (Dict[str, Any], optional): The variables. Defaults to None.
            headers (Dict[str, Any], optional): Additional headers. Defaults to None.
            operation_name (str, optional): The operation_name to executed. Defaults to all.
            **kwargs: Additional arguments to pass to the link chain

        Raises:
            NotConnectedError: An error when the Rath is not connected and autoload is set to false

        Yields:
            Iterator[GraphQLResult]: The result of the query as an async iterator
        """        """"""
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
        self._context_token = current_rath.set(self)
        await self.link.__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        if self._connected:
            await self.adisconnect()

        await self.link.__aexit__(*args, **kwargs)
        self._entered = False
        if self._context_token:
            current_rath.set(None)

    class Config:
        underscore_attrs_are_private = True
