from typing import AsyncIterator
from rath.links.base import AsyncTerminatingLink
from rath.operation import GraphQLResult, Operation


class DirectSucceedingLink(AsyncTerminatingLink):
    """AssertLink is a link that asserts that the operation matches a set of assertions.

    This link is useful for testing.

    """

    async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
        """Executes an operation against the link

        Parameters
        ----------
        operation : Operation
            The operation to execute

        Yields
        ------
        GraphQLResult
            The result of the operation
        """

        yield GraphQLResult(data={})
