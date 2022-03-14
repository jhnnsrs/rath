from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Awaitable, Callable, Coroutine
from rath.links.base import AsyncContinuationLink
from rath.operation import GraphQLResult, Operation
from rath.links.errors import AuthenticationError


async def fake_loader():
    raise Exception("No Token loader specified")


@dataclass
class AuthTokenLink(AsyncContinuationLink):

    token_loader: Callable[[], Awaitable[str]] = field(
        default_factory=lambda: fake_loader
    )
    maximum_refresh_attempts: int = 2
    load_token_on_connect: bool = True

    _token = None

    async def __aenter__(self):
        if self.load_token_on_connect:
            await self.reload_token()

    async def reload_token(self) -> None:
        self.token = await self.token_loader()
        return self.token

    async def aquery(self, operation: Operation, retry=0, **kwargs) -> GraphQLResult:
        operation.context.headers["Authorization"] = f"Bearer {self.token}"
        if not self.token:
            await self.reload_token()
        try:

            return await self.next.aquery(operation, **kwargs)
        except AuthenticationError as e:
            retry = retry + 1
            if retry > self.maximum_refresh_attempts:
                raise AuthenticationError("Maximum refresh attempts reached") from e

            self.token = await self.reload_token()
            return await self.aquery(operation, retry=retry, **kwargs)

    async def asubscribe(
        self, operation: Operation, retry=0, **kwargs
    ) -> AsyncIterator[GraphQLResult]:
        if retry >= self.maximum_refresh_attempts:
            raise AuthenticationError("Maximum refresh attempts reached")

        operation.context.headers["Authorization"] = f"Bearer {self.token}"
        try:
            async for result in self.next.asubscribe(operation, **kwargs):
                yield result

        except AuthenticationError as e:
            async for result in self.asubscribe(operation, retry=retry + 1, **kwargs):
                yield result
