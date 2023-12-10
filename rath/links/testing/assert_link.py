from typing import AsyncIterator, Callable, List
from rath.links.base import AsyncTerminatingLink
from rath.operation import GraphQLResult, Operation


class AssertLink(AsyncTerminatingLink):
    """AssertLink is a link that asserts that the operation matches a set of assertions.

    This link is useful for testing.

    """

    assertions: List[Callable[[Operation], bool]] = []

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
        for assertion in self.assertions:
            assert assertion(
                operation
            ), f"Assertion failed for operation {operation} on {assertion}"

        yield GraphQLResult(data={})
