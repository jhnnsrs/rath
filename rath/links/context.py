import asyncio
from concurrent.futures import ThreadPoolExecutor
from rath.links.base import ContinuationLink
from rath.operation import GraphQLResult, Operation
from koil import unkoil, unkoil_gen, Koil
from koil.helpers import unkoil_gen


class SwitchAsyncLink(ContinuationLink):
    """Swithc Async Link

    Async switches allow to use async resolvers in an sync context.
    It uses the koil library to facilitate the switch.

    Koil can use unstateful links (no "async with" logic), by simply calling
    asyncio.run(). Or spin up a thread with the async logic for stateful links
    (with "async with" logic). It also takes care of stoppin the thread when
    the link is disconnected.

    This allows us to use the same logic for both sync and async links, where
    a connection is required.

    Check the koil documentation to learn more about how koil does it in detail.

    Args:
        ContinuationLink (_type_): _description_
    """

    def __init__(self, **koilparams):
        super().__init__()

    async def aquery(self, operation: Operation, **kwargs) -> GraphQLResult:
        return await self.next.aquery(operation)

    async def asubscribe(self, operation: Operation, **kwargs) -> GraphQLResult:
        async for result in self.next.asubscribe(operation):
            yield result

    def query(self, operation: Operation, **kwargs) -> GraphQLResult:
        return unkoil(self.next.aquery, operation, **kwargs)

    def subscribe(self, operation: Operation, **kwargs) -> GraphQLResult:
        return unkoil_gen(self.next.asubscribe, operation, **kwargs)
