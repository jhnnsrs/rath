from rath.links.base import ContinuationLink
from rath.operation import Operation


class ParsingLink(ContinuationLink):
    async def aparse(self, operation: Operation) -> Operation:
        raise NotImplementedError("Please implement this method")

    async def aexecute(self, operation: Operation, **kwargs) -> Operation:
        operation = await self.aparse(operation)
        async for result in self.next.aexecute(operation, **kwargs):
            yield result
