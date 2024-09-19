from typing import AsyncIterator, Awaitable, Callable

from rath.links.base import ContinuationLink
from rath.operation import GraphQLResult, Operation
from rath.errors import NotComposedError


async def just_print(operation: Operation) -> None:
    """A simple logging function that prints the operation"""
    print(operation)


class LogLink(ContinuationLink):
    """The Log link is a logging
    link that logs the operation to the console.
    links.
    """

    log: Callable[[Operation], Awaitable[None]] = just_print

    async def aexecute(
        self, operation: Operation, **kwargs
    ) -> AsyncIterator[GraphQLResult]:
        """Executes an operation against the link

        This link simply forwards the operation to the next link.
        after logging it.

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

        await self.log(operation)
        async for result in self.next.aexecute(operation, **kwargs):
            yield result
