from typing import Callable
from rath.operation import Operation
from rath.transports.base import Transport


class SplitTransport(Transport):
    def __init__(
        self,
        transport: Transport,
        transport2: Transport,
        split: Callable[[Operation], bool],
    ) -> None:
        super().__init__()
        self.transport = transport
        self.transport2 = transport2
        self.split = split

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
