import asyncio
from typing import AsyncIterator

from rath.links.base import ContinuationLink
from rath.operation import GraphQLResult, Operation
from rath.errors import NotComposedError


async def just_print(operation: Operation) -> None:
    """A simple logging function that prints the operation"""
    print(operation)


class TimeoutLink(ContinuationLink):
    """The Log link is a logging
    link that logs the operation to the console.
    links.
    """

    timeout: float = 20
    """The timeout for the operation in seconds"""

    async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
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

        if not self.timeout:
            async for result in self.next.aexecute(operation):
                yield result

        else:
            aiter = self.next.aexecute(operation).__aiter__()
            try:
                while True:
                    # Wait for the next item from the async iterator
                    try:
                        result = await asyncio.wait_for(aiter.__anext__(), timeout=self.timeout)
                        yield result
                    except StopAsyncIteration:
                        break
            except asyncio.TimeoutError as e:
                raise asyncio.TimeoutError(f"Operation timed out after {self.timeout} seconds") from e
            except Exception as e:
                raise e
