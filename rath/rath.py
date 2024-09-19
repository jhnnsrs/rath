from koil.composition import KoiledModel
from pydantic import Field
from rath.errors import NotConnectedError
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
from contextvars import ContextVar, Token
from koil import unkoil_gen, unkoil


current_rath: ContextVar[Optional["Rath"]] = ContextVar("current_rath", default=None)


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
        from rath.links.retry import RetryLink
        from rathlinks.aiohttp import AIOHttpLink

        retry = RetryLink()
        http = AIOHttpLink(endpoint_url"https://graphql-pokemon.now.sh/graphql")

        rath = Rath(link=compose(retry, link))
        async with rath as r:
            await r.aquery(...)
        ```

    """

    link: TerminatingLink = Field(
        ...,
        description="The terminating link used to send operations to the server. Can be a composed link chain.",
    )
    """The terminating link used to send operations to the server. Can be a composed link chain."""

    _entered = False
    """An internal flag flag that indicates whether the Rath is currently in the context manager."""
    _context_token: Optional[Token] = None
    """A context token that is used to keep track of the current rath in the context manager."""

    async def aquery(
        self,
        query: Union[str, DocumentNode],
        variables: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
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
        op = opify(query, variables, headers, operation_name, **kwargs)

        result = None

        async for data in self.link.aexecute(op):
            result = data
            break

        if not result:
            raise NotConnectedError("Could not retrieve data from the server.")
            # This is to account for the fact that mypy apparently doesn't
            # understand that a return statement in a generator is valid.
            # This is a workaround to make mypy happy.

        return result

    def query(
        self,
        query: Union[str, DocumentNode],
        variables: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
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
        variables: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
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
        variables: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
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
        """

        op = opify(query, variables, headers, operation_name, **kwargs)
        async for data in self.link.aexecute(op):
            yield data

    async def __aenter__(self) -> "Rath":
        """Enters the context manager of the link"""
        self._entered = True
        self._context_token = current_rath.set(self)
        await self.link.__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs) -> None:
        """Exits the context manager of the link"""
        await self.link.__aexit__(*args, **kwargs)
        self._entered = False
        if self._context_token:
            current_rath.set(None)

