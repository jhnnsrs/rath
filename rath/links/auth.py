from typing import AsyncIterator, Awaitable, Callable, Optional

from rath.links.base import ContinuationLink
from rath.operation import GraphQLResult, Operation
from rath.links.errors import (
    AuthenticationError,
    TokenLoaderNotSetError,
    TokenRefresherNotSetError,
)
from rath.errors import NotComposedError


class AuthTokenLink(ContinuationLink):
    """AuthTokenLink is a link that adds an authentication token to the context.
    The authentication token is retrieved by calling the token_loader function.
    If the wrapped link raises an AuthenticationError, the token_refresher function
    is called again to refresh the token.

    This link is statelss, and does not store the token. It is up to the user to
    store the token and pass it to the token_loader function.
    """

    maximum_refresh_attempts: int = 3
    """The maximum number of times the token_refresher function will be called, before the operation fails."""

    load_token_on_connect: bool = True
    """If True, the token_loader function will be called when the link is connected."""
    load_token_on_enter: bool = True
    """If True, the token_loader function will be called when the link is entered."""

    async def aload_token(self, operation: Operation) -> str:
        """A function that loads the authentication token.

        This function should return a string containing the authentication token.

        Parameters
        ----------
        operation : Operation
            The operation to execute

        Raises
        ------
        TokenLoaderNotSetError
            When the token cannot be loaded because no loader is configured
        """
        raise TokenLoaderNotSetError(
            "No Token loader specified. Subclass AuthTokenLink and override aload_token, "
            "or use ComposedAuthLink with a token_loader."
        )

    async def arefresh_token(self, operation: Operation) -> str:
        """A function that refreshes the authentication token.

        This function should return a string containing the authentication token.
        In comparison to the token_loader function, this function is called when
        the server already raised an AuthenticationError, so a refresh should really
        be attempted.

        Parameters
        ----------
        operation : Operation
            The operation to execute

        Raises
        ------
        TokenRefresherNotSetError
            When the token cannot be refreshed because no refresher is configured
        """
        raise TokenRefresherNotSetError(
            "No Token refresher specified. Subclass AuthTokenLink and override arefresh_token, "
            "or use ComposedAuthLink with a token_refresher."
        )

    async def aexecute(
        self, operation: Operation, retry: int = 0
    ) -> AsyncIterator[GraphQLResult]:
        """Executes and forwards an operation to the next link.

        This method will add the authentication token to the context of the operation,
        and will refresh the token if the next link raises an AuthenticationError, until
        the maximum number of refresh attempts is reached.

        Parameters
        ----------
        operation : Operation
            The operation to execute

        Yields
        ------
        GraphQLResult
            The result of the operation
        """
        if not self.next:
            raise NotComposedError("No next link set")

        token = await self.aload_token(operation)
        operation.context.headers["Authorization"] = f"Bearer {token}"
        operation.context.initial_payload["token"] = token

        try:
            async for result in self.next.aexecute(operation):
                yield result

        except AuthenticationError as e:
            if retry >= self.maximum_refresh_attempts:
                raise AuthenticationError("Maximum refresh attempts reached") from e

            await self.arefresh_token(operation)

            async for result in self.aexecute(operation, retry=retry + 1):
                yield result


class ComposedAuthLink(AuthTokenLink):
    """A composed version of the AuthTokenLink.

    This link is a composed link that allows to set the token_loader and token_refresher
    functions as composition elements not as class attributes.
    """

    token_loader: Optional[Callable[[], Awaitable[str]]] = None
    """The function used to load the authentication token. This function should
        return a string containing the authentication token."""
    token_refresher: Optional[Callable[[], Awaitable[str]]] = None
    """The function used to refresh the authentication token. This function should
        return a string containing the authentication token."""

    async def aload_token(self, operation: Operation) -> str:
        """Forwards the operation to the token_loader function."""
        if self.token_loader is None:
            raise TokenLoaderNotSetError(
                "No Token loader specified. Pass a token_loader to ComposedAuthLink."
            )
        return await self.token_loader()

    async def arefresh_token(self, operation: Operation) -> str:
        """Forwards the operation to the token_refresher function."""
        if self.token_refresher is None:
            raise TokenRefresherNotSetError(
                "No Token refresher specified. Pass a token_refresher to ComposedAuthLink."
            )
        return await self.token_refresher()
