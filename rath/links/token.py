from multiprocessing import AuthenticationError
from rath.links.base import Link, ContinuationLink
from rath.operation import GraphQLResult, Operation


class TokenContinuationLink(ContinuationLink):
    def __init__(self, token="", maximum_refresh_attempts=3) -> None:
        self.token = token
        self.maximum_refresh_attempts = maximum_refresh_attempts

    async def reload_token(self) -> None:
        self.token = "new token"

    async def aquery(self, operation: Operation, retry=0) -> GraphQLResult:
        if retry >= self.maximum_refresh_attempts:
            raise AuthenticationError("Maximum refresh attempts reached")

        operation.context.headers["Authorization"] = f"Bearer {self.token}"
        try:
            return await self.next.aquery(operation)
        except Exception as e:
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
        print("Called aconnect")
