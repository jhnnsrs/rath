from typing import AsyncIterator

from rath.links.base import ContinuationLink
from rath.operation import GraphQLResult, Operation
from rath.errors import NotComposedError


class ForwardLink(ContinuationLink):
    """The Forward link is a void link
    that simply forwards the operation to the next link.

    This link is useful for conditional fallbacks for other
    links.
    """

    async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
        """Executes an operation against the link

        This link simply forwards the operation to the next link.


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

        async for result in self.next.aexecute(operation):
            yield result

