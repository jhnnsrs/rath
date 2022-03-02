from rath.links.base import ContinuationLink
from rath.operation import Operation


class ParsingLink(ContinuationLink):
    def parse(self, operation: Operation) -> Operation:
        raise NotImplementedError("Please implement this method")

    def aparse(self, operation: Operation) -> Operation:
        raise NotImplementedError("Please implement this method")

    async def aquery(self, operation: Operation, **kwargs) -> Operation:
        operation = await self.aparse(operation)
        return await self.next.aquery(operation, **kwargs)

    async def asubscribe(self, operation: Operation, **kwargs) -> Operation:
        operation = await self.aparse(operation)
        async for result in self.next.asubscribe(operation, **kwargs):
            yield result

    def query(self, operation: Operation, **kwargs) -> Operation:
        operation = self.parse(operation)
        return self.next.query(operation, **kwargs)

    def subscribe(self, operation: Operation, **kwargs) -> Operation:
        operation = self.parse(operation)
        return self.next.subscribe(operation, **kwargs)
