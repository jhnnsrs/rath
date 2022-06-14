from typing import Callable

from pydantic import Field
from rath.operation import Operation
from rath.links.base import TerminatingLink


class SplitLink(TerminatingLink):
    left: TerminatingLink
    right: TerminatingLink
    split: Callable[[Operation], bool] = Field(exclude=True)

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
