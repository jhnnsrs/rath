from typing import AsyncIterator, Awaitable, Callable, Optional

from pydantic import Field
from rath.links.base import ContinuationLink
from rath.operation import GraphQLResult, Operation
from rath.links.errors import AuthenticationError


async def fake_loader():
    raise Exception("No Token loader specified")


class AuthTokenLink(ContinuationLink):
    """AuthTokenLink is a link that adds an authentication token to the context.
    The authentication token is retrieved by calling the token_loader function.
    If the wrapped link raises an AuthenticationError, the token_refresher function
    is called again to refresh the token.

    This link is statelss, and does not store the token. It is up to the user to
    store the token and pass it to the token_loader function.
    """

    token_loader: Callable[[], Awaitable[str]]
    """The function used to load the authentication token. This function should
        return a string containing the authentication token."""
    token_refresher: Callable[[], Awaitable[str]]
    """The function used to refresh the authentication token. This function should
        return a string containing the authentication token."""

    maximum_refresh_attempts: int = 3
    """The maximum number of times the token_refresher function will be called, before the operation fails."""

    load_token_on_connect: bool = True
    """If True, the token_loader function will be called when the link is connected."""
    load_token_on_enter: bool = True
    """If True, the token_loader function will be called when the link is entered."""

    async def aconnect(self):
        if self.load_token_on_connect:
            await self.token_loader()

    async def aexecute(
        self, operation: Operation, retry=0, **kwargs
    ) -> AsyncIterator[GraphQLResult]:

        operation.context.headers[
            "Authorization"
        ] = f"Bearer {await self.token_loader()}"
        try:

            async for result in self.next.aexecute(operation, **kwargs):
                yield result

        except AuthenticationError as e:
            retry = retry + 1
            operation.context.headers[
                "Authorization"
            ] = f"Bearer {await self.token_refresher()}"
            if retry > self.maximum_refresh_attempts:
                raise AuthenticationError("Maximum refresh attempts reached") from e

            async for result in self.aexecute(operation, retry=retry + 1, **kwargs):
                yield result

    class Config:
        underscore_attrs_are_private = True
        arbitary_types_allowed = True
