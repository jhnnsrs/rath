from typing import AsyncIterator, Awaitable, Callable

from pydantic import Field
from rath.links.base import ContinuationLink
from rath.operation import GraphQLResult, Operation
from rath.links.errors import AuthenticationError


async def fake_loader():
    raise Exception("No Token loader specified")


class AuthTokenLink(ContinuationLink):

    token_loader: Callable[[], Awaitable[str]] = Field(
        default_factory=lambda: fake_loader, exclude=True
    )
    maximum_refresh_attempts: int = 2
    load_token_on_connect: bool = True

    _token: str = None

    async def __aenter__(self):
        if self.load_token_on_connect:
            await self.reload_token()

    async def reload_token(self) -> None:
        self._token = await self.token_loader()
        return self._token

    async def aexecute(
        self, operation: Operation, retry=0, **kwargs
    ) -> AsyncIterator[GraphQLResult]:

        operation.context.headers["Authorization"] = f"Bearer {self._token}"
        if not self._token:
            await self.reload_token()
        try:

            async for result in self.next.aexecute(operation, **kwargs):
                yield result

        except AuthenticationError as e:
            retry = retry + 1
            if retry > self.maximum_refresh_attempts:
                raise AuthenticationError("Maximum refresh attempts reached") from e

            async for result in self.aexecute(operation, retry=retry + 1, **kwargs):
                yield result

    class Config:
        underscore_attrs_are_private = True
        arbitary_types_allowed = True
