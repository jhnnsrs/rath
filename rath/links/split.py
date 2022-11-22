from typing import Callable

from pydantic import Field
from rath.operation import Operation
from rath.links.base import TerminatingLink


class SplitLink(TerminatingLink):
    """SplitLink is a link that splits the operation into two paths. The operation is sent to the left path if the predicate returns true, otherwise to the right path.
    
    This is useful for exampole when implementing a cache link, where the operation is sent to the cache if it is a query, and to the network if it is a mutation.
    Or when subscriptions and queries are sent to different links (e.g. a websocket link and a http link)."""
    left: TerminatingLink
    """The link that is used if the predicate returns true."""
    right: TerminatingLink
    """The link that is used if the predicate returns false."""
    split: Callable[[Operation], bool] = Field(exclude=True)
    """The function used to split the operation. This function should return a boolean. If true, the operation is sent to the left path, otherwise to the right path."""

    async def aexecute(self, operation: Operation, **kwargs) -> Operation:
        iterator = (
            self.left.aexecute(operation, **kwargs)
            if self.split(operation)
            else self.right.aexecute(operation, **kwargs)
        )

        async for res in iterator:
            yield res

    async def aconnect(self):
        await self.left.aconnect()
        await self.right.aconnect()

    async def adisconnect(self):
        await self.left.adisconnect()
        await self.right.adisconnect()

    async def __aenter__(self):
        await self.left.__aenter__()
        await self.right.__aenter__()

    async def __aexit__(self, *args, **kwargs):
        await self.left.__aexit__(*args, **kwargs)
        await self.right.__aexit__(*args, **kwargs)


def split(
    left: TerminatingLink, right: TerminatingLink, split: Callable[[Operation], bool]
):
    """
    Splits a Link into two paths. Acording to a predicate function. If predicate returns
    true, the operation is sent to the left path, otherwise to the right path.
    """
    return SplitLink(left=left, right=right, split=split)
