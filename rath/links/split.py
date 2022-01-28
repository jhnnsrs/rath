from typing import Callable, List
from rath.operation import Operation
from rath.links.base import ContinuationLink, Link, TerminatingLink, Transport


class SplitTransport(TerminatingLink):
    def __init__(
        self,
        left: List[Link],
        right: List[Link],
        split: Callable[[Operation], bool],
    ) -> None:
        super().__init__()
        self.transport = transport
        self.transport2 = transport2
        self.split = split

    async def __call__(self, rath):
        return super().__call__(rath)

    async def aconnect(self) -> None:
        await self.transport.aconnect()
        await self.transport2.aconnect()

    async def aquery(self, operation: Operation) -> Operation:
        future = (
            self.transport.aquery(operation)
            if self.split(operation)
            else self.transport2.aquery(operation)
        )
        return await future

    def asubscribe(self, operation: Operation) -> Operation:
        future = (
            self.transport.asubscribe(operation)
            if self.split(operation)
            else self.transport2.asubscribe(operation)
        )
        return future


def split(
    transport: Transport, transport2: Transport, split: Callable[[Operation], bool]
):
    return SplitTransport(transport, transport2, split)
