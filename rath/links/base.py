from typing import AsyncIterator, Iterator
from rath.operation import GraphQLResult, Operation


class Link:
    def connect(self) -> None:
        pass

    def disconnect(self) -> None:
        pass

    async def aconnect(self) -> None:
        pass

    async def adisconnect(self) -> None:
        pass

    async def aquery(self, operation: Operation) -> GraphQLResult:
        raise NotImplementedError(
            f"Please overwrite the aquery method in {self.__class__.__name__}"
        )

    async def asubscribe(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
        raise NotImplementedError(
            f"Please overwrite the asubscribe method in {self.__class__.__name__}"
        )

    def query(self, operation: Operation) -> GraphQLResult:
        raise NotImplementedError(
            f"Please overwrite the query method in {self.__class__.__name__}"
        )

    def subscribe(self, operation: Operation) -> Iterator[GraphQLResult]:
        raise NotImplementedError(
            f"Please overwrite the subscribe method in {self.__class__.__name__}"
        )


class TerminatingLink(Link):
    def __call__(self, rath):
        self.rath = rath
        return self

    async def aconnect(self) -> None:
        pass

    async def adisconnect(self) -> None:
        pass

    def connect(self) -> None:
        pass

    def disconnect(self) -> None:
        pass


class AsyncTerminatingLink(TerminatingLink):
    def query(self, operation: Operation) -> GraphQLResult:
        raise NotImplementedError(
            "Async Terminating link does not support syncrhonous queries. Please compose together with a context switch link"
        )

    def subscribe(self, operation: Operation) -> Iterator[GraphQLResult]:
        raise NotImplementedError(
            "Async Terminating link does not support syncrhonous queries. Please compose together with a context switch link"
        )


class SyncTerminatingLink(TerminatingLink):
    async def aquery(self, operation: Operation) -> GraphQLResult:
        raise NotImplementedError(
            "Sync Terminating link does not support asynchronous queries. Please compose together with a context switch link"
        )

    async def asubscribe(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
        raise NotImplementedError(
            "Sync Terminating link does not support asynchronous queries. Please compose together with a context switch link"
        )


class ContinuationLink(Link):
    def __call__(self, rath, next: Link):
        self.rath = rath
        self.next = next
        return self

    async def aconnect(self) -> None:
        await self.next.aconnect()

    async def adisconnect(self) -> None:
        await self.next.adisconnect()

    def connect(self) -> None:
        self.next.connect()

    def disconnect(self) -> None:
        self.next.disconnect()


class AsyncContinuationLink(ContinuationLink):
    def query(self, operation: Operation) -> GraphQLResult:
        raise NotImplementedError(
            "Async Terminating link does not support syncrhonous queries. Please compose together with a context switch link"
        )

    def subscribe(self, operation: Operation) -> Iterator[GraphQLResult]:
        raise NotImplementedError(
            "Async Terminating link does not support syncrhonous queries. Please compose together with a context switch link"
        )


class SyncContinuationLink(ContinuationLink):
    async def aquery(self, operation: Operation) -> GraphQLResult:
        raise NotImplementedError(
            "Sync Terminating link does not support asynchronous queries. Please compose together with a context switch link"
        )

    async def asubscribe(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
        raise NotImplementedError(
            "Sync Terminating link does not support asynchronous queries. Please compose together with a context switch link"
        )
