from dataclasses import dataclass
from typing import Callable, List
from rath.operation import Operation
from rath.links.base import TerminatingLink


@dataclass
class SplitLink(TerminatingLink):
    left: TerminatingLink
    right: TerminatingLink
    split: Callable[[Operation], bool]

    def __call__(self, rath):
        self.left(rath)
        self.right(rath)

    async def aquery(self, operation: Operation, **kwargs) -> Operation:
        future = (
            self.left.aquery(operation, **kwargs)
            if self.split(operation)
            else self.right.aquery(operation, **kwargs)
        )
        return await future

    async def asubscribe(self, operation: Operation, **kwargs) -> Operation:
        iterator = (
            self.left.asubscribe(operation, **kwargs)
            if self.split(operation)
            else self.right.asubscribe(operation, **kwargs)
        )

        async for res in iterator:
            yield res

    def query(self, operation: Operation, **kwargs) -> Operation:
        future = (
            self.left.query(operation, **kwargs)
            if self.split(operation)
            else self.right.query(operation, **kwargs)
        )

        return future

    def subscribe(self, operation: Operation, **kwargs) -> Operation:
        iterator = (
            self.left.subscribe(operation, **kwargs)
            if self.split(operation)
            else self.right.subscribe(operation, **kwargs)
        )

        return iterator

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
    return SplitLink(left, right, split)
