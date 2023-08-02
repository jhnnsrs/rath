from typing import AsyncIterator, Awaitable, Callable, Optional

from pydantic import Field
from rath.links.base import ContinuationLink
from rath.operation import GraphQLResult, Operation
from rath.links.errors import AuthenticationError


class ForwardLink(ContinuationLink):
    """The Forward link is a void link
    that simply forwards the operation to the next link.

    This link is useful for conditional fallbacks for other
    links.
    """

    async def aexecute(
        self, operation: Operation, **kwargs
    ) -> AsyncIterator[GraphQLResult]:
        async for result in self.next.aexecute(operation, **kwargs):
            yield result

    class Config:
        underscore_attrs_are_private = True
        arbitary_types_allowed = True
