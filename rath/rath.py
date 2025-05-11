from koil.composition import KoiledModel
from pydantic import Field, field_validator
from rath.errors import NotConnectedError
from rath.links.base import Link, TerminatingLink, ContinuationLink
from typing import (
    AsyncGenerator,
    Dict,
    Any,
    Generator,
    Optional,
    Type,
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
    _context_token: Optional[Token[Optional["Rath"]]] = None
    """A context token that is used to keep track of the current rath in the context manager."""

    @field_validator("link", mode="before")
    def validate_link(cls, link: TerminatingLink | list[ContinuationLink | TerminatingLink] | Any) -> TerminatingLink:
        """Validates the link and ensures it is a terminating link or a list of links."""
        if isinstance(link, list):
            # If the link is a list, we assume it is a chain of links
            # and we compose them into a single link
            from rath.links.compose import compose

            for lin in link:  # type: ignore
                if not isinstance(lin, (ContinuationLink, TerminatingLink)):
                    raise ValueError("All links in the list must be of type Link")

            if not isinstance(link[-1], TerminatingLink):
                raise ValueError("The last link in the list must be a TerminatingLink")

            return compose(*link)  # type: ignore

        if not isinstance(link, TerminatingLink):
            raise ValueError("Link must be a TerminatingLink or a list of TerminatingLinks")

        return link

    async def aquery(
        self,
        query: Union[str, DocumentNode],
        variables: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
        **kwargs: Any,
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
        **kwargs: Any,
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
        return unkoil(self.aquery, query, variables, headers, operation_name)

    def subscribe(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
        **kwargs: Any,
    ) -> Generator[GraphQLResult, None, None]:
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
        return unkoil_gen(self.asubscribe, query, variables, headers, operation_name, **kwargs)

    async def asubscribe(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncGenerator[GraphQLResult, None]:
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

    async def __aexit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], traceback: Optional[Any]) -> None:
        """Exits the context manager of the link"""
        await self.link.__aexit__(exc_type, exc_val, traceback)
        self._entered = False
        if self._context_token:
            current_rath.set(None)
