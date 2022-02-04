import asyncio
from concurrent.futures import ThreadPoolExecutor
from koil.loop import koil_gen
from rath.links.base import ContinuationLink
from rath.operation import GraphQLResult, Operation
from koil import koil


class SwitchAsyncLink(ContinuationLink):
    async def aquery(self, operation: Operation) -> GraphQLResult:
        return self.next.aquery(operation)

    async def asubscibe(self, operation: Operation) -> GraphQLResult:
        async for result in self.next.aconnect(operation):
            yield result

    def query(self, operation: Operation) -> GraphQLResult:
        return koil(self.next.aquery(operation))

    def subscribe(self, operation: Operation) -> GraphQLResult:
        for result in koil_gen(self.next.asubscribe(operation)):
            yield result


class SwitchSyncLink(ContinuationLink):
    def __init__(self, excecutor=None) -> None:
        self.excecutor = excecutor or ThreadPoolExecutor()
        super().__init__()

    async def aconnect(self) -> None:
        self.e = self.excecutor.__enter__()

    async def aquery(self, operation: Operation) -> GraphQLResult:
        return await asyncio.wrap_future(self.e.submit(self.next.query, operation))

    async def asubscibe(self, operation: Operation) -> GraphQLResult:
        raise NotImplementedError(
            "We need to fiqure this out yet. Normally a __next__ call here would be enough"
        )

    def query(self, operation: Operation) -> GraphQLResult:
        return self.next.query(operation)

    def subscribe(self, operation: Operation) -> GraphQLResult:
        for result in self.next.subscribe(operation):
            yield result
