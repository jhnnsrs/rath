from typing import AsyncIterator, Callable
from rath.links.base import AsyncTerminatingLink
from rath.operation import GraphQLResult, Operation


class AssertLink(AsyncTerminatingLink):
    assertions: list[Callable[[Operation], bool]] = []

    async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
        for assertion in self.assertions:
            assert assertion(
                operation
            ), f"Assertion failed for operation {operation} on {assertion}"

        yield GraphQLResult(data={})
