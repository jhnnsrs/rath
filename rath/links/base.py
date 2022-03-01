from typing import AsyncIterator, Iterator
from rath.operation import GraphQLResult, Operation


class Link:
    async def __aenter__(self) -> None:
        pass

    async def __aexit__(self, *args, **kwargs) -> None:
        pass

    def __enter__(self) -> None:
        pass

    def __exit__(self, *args, **kwargs) -> None:
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

    async def __aenter__(self) -> None:
        pass

    async def __aexit__(self, *args, **kwargs) -> None:
        pass

    def __enter__(self) -> None:
        pass

    def __exit__(self, *args, **kwargs) -> None:
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

    async def __aenter__(self) -> None:
        return await self.next.__aenter__()

    async def __aexit__(self, *args, **kwargs) -> None:
        return await self.next.__aexit__(*args, **kwargs)

    def __enter__(self) -> None:
        self.next.__enter__()

    def __exit__(self, *args, **kwargs) -> None:
        self.next.__exit__(*args, **kwargs)


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
