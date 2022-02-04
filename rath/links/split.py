from typing import Callable, List
from koil.loop import koil, koil_gen
from rath.operation import Operation
from rath.links.base import TerminatingLink


class SplitTransport(TerminatingLink):
    def __init__(
        self,
        left: TerminatingLink,
        right: TerminatingLink,
        split: Callable[[Operation], bool],
    ) -> None:
        super().__init__()
        assert isinstance(left, TerminatingLink), "left must be a TerminatingLink"
        assert isinstance(right, TerminatingLink), "left must be a TerminatingLink"
        self.left = left
        self.right = right
        self.split = split

    async def __call__(self, rath):
        self.left(rath)
        self.right(rath)

    async def aconnect(self) -> None:
        await self.left.aconnect()
        await self.right.aconnect()

    async def aquery(self, operation: Operation) -> Operation:
        future = (
            self.left.aquery(operation)
            if self.split(operation)
            else self.right.aquery(operation)
        )
        return await future

    async def asubscribe(self, operation: Operation) -> Operation:
        iterator = (
            self.left.asubscribe(operation)
            if self.split(operation)
            else self.right.asubscribe(operation)
        )

        async for res in iterator:
            yield res

    def query(self, operation: Operation) -> Operation:
        future = (
            self.left.aquery(operation)
            if self.split(operation)
            else self.right.aquery(operation)
        )

        return koil(future)

    def subscribe(self, operation: Operation) -> Operation:
        iterator = (
            self.left.asubscribe(operation)
            if self.split(operation)
            else self.right.asubscribe(operation)
        )

        for res in koil_gen(iterator):
            yield res


def split(
    left: TerminatingLink, right: TerminatingLink, split: Callable[[Operation], bool]
):
    """
    Splits a Link into two paths. Acording to a predicate function. If predicate returns
    true, the operation is sent to the left path, otherwise to the right path.
    """
    return SplitTransport(left, right, split)
