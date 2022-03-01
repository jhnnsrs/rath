import asyncio
from concurrent.futures import ThreadPoolExecutor
from rath.links.base import ContinuationLink
from rath.operation import GraphQLResult, Operation
from koil import unkoil, unkoil_gen, Koil


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
        self.__koil = Koil(**koilparams)

    async def aquery(self, operation: Operation) -> GraphQLResult:
        return await self.next.aquery(operation)

    async def asubscribe(self, operation: Operation) -> GraphQLResult:
        async for result in self.next.asubscribe(operation):
            yield result

    def query(self, operation: Operation) -> GraphQLResult:
        return unkoil(self.next.aquery, operation)

    def subscribe(self, operation: Operation) -> GraphQLResult:
        for result in unkoil_gen(self.next.asubscribe, operation):
            yield result

    def __enter__(self) -> None:
        self.__koil.__enter__()  # spin up a new thread if needed (if we are already in a koiled environment, use that one)
        unkoil(self.next.__aenter__)

    def __exit__(self, *args, **kwargs) -> None:
        unkoil(self.next.__aexit__, *args, **kwargs)
        self.__koil.__exit__(None, None, None)  # cleanup thread if we had to spin it up


class SwitchSyncLink(ContinuationLink):
    def __init__(self, excecutor=None) -> None:
        self.excecutor = excecutor or ThreadPoolExecutor()
        self._lock = asyncio.Lock()
        self.connected = False
        super().__init__()

    async def __aenter__(self) -> None:
        self.e = self.excecutor.__enter__()
        self.next.__enter__()
        self.connected = True

    async def aquery(self, operation: Operation) -> GraphQLResult:
        async with self._lock:
            if not self.connected:
                await self.aconnect()

        return await asyncio.wrap_future(self.e.submit(self.next.query, operation))

    async def asubscribe(self, operation: Operation) -> GraphQLResult:
        raise NotImplementedError(
            "We need to fiqure this out yet. Normally a __next__ call here would be enough"
        )

    def query(self, operation: Operation) -> GraphQLResult:
        return self.next.query(operation)

    def subscribe(self, operation: Operation) -> GraphQLResult:
        for result in self.next.subscribe(operation):
            yield result

    async def __aexit__(self, *args, **kwargs) -> None:
        self.e = self.excecutor.__exit__()
        self.next.__exit__(*args, **kwargs)
        self.connected = False
