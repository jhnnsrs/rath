from typing import AsyncIterator, Awaitable, Callable, Optional

from pydantic import Field
from rath.links.base import ContinuationLink
from rath.operation import GraphQLResult, Operation
from rath.links.errors import AuthenticationError


async def just_print(operation: Operation):
    print(operation)


class LogLink(ContinuationLink):
    """The Log link is a logging
    link that logs the operation to the console.
    links.
    """

    log: Callable[[Operation], Awaitable[None]] = just_print

    async def aconnect(self):
        pass

    async def aexecute(
        self, operation: Operation, **kwargs
    ) -> AsyncIterator[GraphQLResult]:
        await self.log(operation)
        async for result in self.next.aexecute(operation, **kwargs):
            yield result

    class Config:
        underscore_attrs_are_private = True
        arbitary_types_allowed = True