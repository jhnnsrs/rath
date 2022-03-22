from typing import AsyncIterator, Iterator, Optional
from koil.composition import KoiledModel
from rath.operation import GraphQLResult, Operation
from koil import unkoil, unkoil_gen


class Link(KoiledModel):
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
    pass


class AsyncTerminatingLink(TerminatingLink):
    """An Async Termination Link

    This is a link that terminates the query or subscription, aka
    it is a link that does not have a next link. It normally
    is used to make network requests with the already parsed
    operations

    Args:
        TerminatingLink (_type_): _description_
    """

    async def aquery(self, operation: Operation) -> GraphQLResult:
        raise NotImplementedError("Your Async Transport needs to overwrite this method")

    async def asubscribe(self, operation: Operation) -> Iterator[GraphQLResult]:
        raise NotImplementedError("Your Async Transport needs to overwrite this method")

    def query(self, operation: Operation, **kwargs) -> GraphQLResult:
        return unkoil(self.aquery, operation, **kwargs)

    def subscribe(self, operation: Operation, **kwargs) -> GraphQLResult:
        return unkoil_gen(self.asubscribe, operation, **kwargs)


class SyncTerminatingLink(TerminatingLink):
    """A Sync Terminating Link

    This is a link that terminates the query or subscription, aka
    it is a link that does not have a next link. It normally
    is used to make network requests with the already parsed
    operations

    """

    async def aquery(self, operation: Operation) -> GraphQLResult:
        raise NotImplementedError(
            "Sync Terminating link does not support asynchronous queries. Please compose together with a context switch link"
        )

    async def asubscribe(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
        raise NotImplementedError(
            "Sync Terminating link does not support asynchronous queries. Please compose together with a context switch link"
        )


class ContinuationLink(Link):
    next: Optional[Link] = None

    def set_next(self, next: Link):
        self.next = next

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
