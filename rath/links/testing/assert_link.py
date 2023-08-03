from typing import AsyncIterator, Callable, List
from rath.links.base import AsyncTerminatingLink
from rath.operation import GraphQLResult, Operation


class AssertLink(AsyncTerminatingLink):
    assertions: List[Callable[[Operation], bool]] = []

    async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
        for assertion in self.assertions:
            assert assertion(
                operation
            ), f"Assertion failed for operation {operation} on {assertion}"

        yield GraphQLResult(data={})
