from typing import AsyncIterator, Iterator
from rath.links.errors import LinkNotConnectedError
from rath.operation import GraphQLResult, Operation
from koil import unkoil, unkoil_gen


class Link:
    async def __aenter__(self) -> None:
        pass

    async def __aexit__(self, *args, **kwargs) -> None:
        pass

    async def aquery(self, operation: Operation, **kwargs) -> GraphQLResult:
        raise NotImplementedError(
            f"Please overwrite the aquery method in {self.__class__.__name__}"
        )

    async def asubscribe(
        self, operation: Operation, **kwargs
    ) -> AsyncIterator[GraphQLResult]:
        raise NotImplementedError(
            f"Please overwrite the asubscribe method in {self.__class__.__name__}"
        )

    def query(self, operation: Operation, **kwargs) -> GraphQLResult:
        raise NotImplementedError(
            f"Please overwrite the query method in {self.__class__.__name__}"
        )

    def subscribe(self, operation: Operation, **kwargs) -> Iterator[GraphQLResult]:
        raise NotImplementedError(
            f"Please overwrite the subscribe method in {self.__class__.__name__}"
        )


class TerminatingLink(Link):
    def __call__(self, rath):
        self.rath = rath
        return self


class AsyncTerminatingLink(TerminatingLink):
    def aquery(self, operation: Operation) -> GraphQLResult:
        raise NotImplementedError("Your Async Transport needs to overwrite this method")

    def asubscribe(self, operation: Operation) -> Iterator[GraphQLResult]:
        raise NotImplementedError("Your Async Transport needs to overwrite this method")

    def query(self, operation: Operation, **kwargs) -> GraphQLResult:
        return unkoil(self.aquery, operation, **kwargs)

    def subscribe(self, operation: Operation, **kwargs) -> GraphQLResult:
        return unkoil_gen(self.asubscribe, operation, **kwargs)


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
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._next = None

    def __call__(self, rath, next: Link):
        self.rath = rath
        self._next = next
        return self

    @property
    def next(self):
        if self._next is None:
            raise LinkNotConnectedError(
                "Next link is not set. This means we were never connected. Please use rath in an async context"
            )
        return self._next

    async def aquery(self, operation: Operation, **kwargs) -> GraphQLResult:
        return await self.next.aquery(operation, **kwargs)

    async def asubscribe(self, operation: Operation, **kwargs) -> GraphQLResult:
        async for x in self.next.asubscribe(operation, **kwargs):
            yield x

    def query(self, operation: Operation, **kwargs) -> GraphQLResult:
        return self.next.query(operation, **kwargs)

    def subscribe(self, operation: Operation, **kwargs) -> GraphQLResult:
        return self.next.subscribe(operation, **kwargs)


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
