from rath.links.base import ContinuationLink
from rath.operation import GraphQLResult, Operation
from typing import AsyncIterator, Awaitable, Callable
from rath.errors import NotComposedError

class ParsingLink(ContinuationLink):
    """ParsingLink is a link that parses operation and returns a new operation.
    It is an abstract class that needs to be implemented by the user.
    """

    async def aparse(self, operation: Operation) -> Operation:
        raise NotImplementedError("Please implement this method")

    async def aexecute(self, operation: Operation, **kwargs) -> AsyncIterator[GraphQLResult]:
        if not self.next:
            raise NotComposedError("No next link set")

        operation = await self.aparse(operation)
        async for result in self.next.aexecute(operation, **kwargs):
            yield result
