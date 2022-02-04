from typing import Any, Coroutine
from rath.links.base import AsyncContinuationLink
from rath.operation import GraphQLResult, Operation
from rath.links.errors import AuthenticationError


async def fake_loader():
    raise Exception("No Token loader specified")


class AuthTokenLink(AsyncContinuationLink):
    def __init__(
        self,
        token_loader: Coroutine[Any, Any, str] = fake_loader,
        maximum_refresh_attempts=3,
        load_token_on_connect=True,
    ) -> None:
        self.token_loader = token_loader
        self.load_token_on_connect = load_token_on_connect
        self.maximum_refresh_attempts = maximum_refresh_attempts
        self.token = None

    async def reload_token(self) -> None:
        self.token = await self.token_loader()
        return self.token

    async def aquery(self, operation: Operation, retry=0) -> GraphQLResult:

        operation.context.headers["Authorization"] = f"Bearer {self.token}"
        try:
            return await self.next.aquery(operation)
        except AuthenticationError as e:
            if retry >= self.maximum_refresh_attempts:
                raise AuthenticationError("Maximum refresh attempts reached") from e

            self.token = await self.reload_token()
            return await self.aquery(operation, retry=retry + 1)

    async def asubscribe(self, operation: Operation, retry=0) -> GraphQLResult:
        if retry >= self.maximum_refresh_attempts:
            raise AuthenticationError("Maximum refresh attempts reached")

        operation.context.headers["Authorization"] = f"Bearer {self.token}"
        try:
            async for result in self.next.asubscribe(operation):
                yield result

        except AuthenticationError as e:
            async for result in self.asubscribe(operation, retry=retry + 1):
                yield result

    async def aconnect(self) -> None:
        if self.load_token_on_connect:
            self.token = await self.token_loader()
