from typing import AsyncIterator, Optional
from koil.composition import KoiledModel
from rath.operation import GraphQLResult, Operation


class Link(KoiledModel):
    async def aconnect(self):
        pass

    async def adisconnect(self):
        pass

    async def __aenter__(self) -> None:
        pass

    async def __aexit__(self, *args, **kwargs) -> None:
        pass

    def aexecute(self, operation: Operation, **kwargs) -> AsyncIterator[GraphQLResult]:
        raise NotImplementedError(
            f"Please overwrite the asubscribe method in {self.__class__.__name__}"
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

    async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
        raise NotImplementedError("Your Async Transport needs to overwrite this method")


class ContinuationLink(Link):
    next: Optional[Link] = None

    def set_next(self, next: Link):
        self.next = next

    async def aexecute(self, operation: Operation, **kwargs) -> GraphQLResult:
        async for x in self.next.aexecute(operation, **kwargs):
            yield x
