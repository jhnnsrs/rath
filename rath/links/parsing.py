from rath.links.base import ContinuationLink
from rath.operation import Operation


class ParsingLink(ContinuationLink):
    def parse(self, operation: Operation) -> Operation:
        raise NotImplementedError("Please implement this method")

    def aparse(self, operation: Operation) -> Operation:
        raise NotImplementedError("Please implement this method")

    async def aquery(self, operation: Operation) -> Operation:
        operation = self.aparse(operation)
        return await self.next.aquery(operation)

    async def asubscribe(self, operation: Operation) -> Operation:
        operation = self.aparse(operation)
        async for result in self.next.asubscribe(operation):
            yield result

    def query(self, operation: Operation) -> Operation:
        operation = self.parse(operation)
        return self.next.query(operation)

    def subscribe(self, operation: Operation) -> Operation:
        operation = self.parse(operation)
        for result in self.next.subscribe(operation):
            yield result
