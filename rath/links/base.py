from typing import AsyncIterator, Optional
from koil.composition import KoiledModel
from rath.operation import GraphQLResult, Operation
from rath.errors import NotComposedError


class Link(KoiledModel):
    """A Link is a class that can be used to send operations to a GraphQL API.
    its main method is aexecute, which takes an operation and returns an
    AsyncIterator of GraphQLResults.

    Links can be composed to form a chain of links. The last link in the chain
    is the terminating link, which is responsible for sending the operation to
    the server.

    """

    async def aconnect(self, operation: Operation) -> None:
        """A coroutine that is called when the link is connected."""
        pass

    async def adisconnect(self) -> None:
        """A coroutine that is called when the link is disconnected."""
        pass

    async def __aenter__(self) -> None:
        """A coroutine that is called when the link is entered."""
        pass

    async def __aexit__(self, *args, **kwargs) -> None:
        """A coroutine that is called when the link is exited."""
        pass

    def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
        """A coroutine that takes an operation and returns an AsyncIterator
        of GraphQLResults. This method should be implemented by subclasses."""
        raise NotImplementedError(
            f"Please overwrite the asubscribe method in {self.__class__.__name__}"
        )


class TerminatingLink(Link):
    """TerminatingLink

    This link type is responsible for sending the operation to the server.

    The last link in a link chain MUST always a TerminatingLink. It cannot delegate the operation
    to another link.
    """


class AsyncTerminatingLink(TerminatingLink):
    """An Async Termination Link

    This is a link that terminates the query or subscription, aka
    it is a link that does not have a next link. It normally
    is used to make network requests with the already parsed
    operations

    Args:
        TerminatingLink (_type_): _description_
    """

    def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
        """Executes an operation against the link

        This is the main method of the link. It takes an operation and returns an AsyncIterator
        of GraphQLResults. This method should be implemented by subclasses. It is important
        that even if the operation is a query or mutation, this method should return an AsyncIterator
        (even if it only yields one result).

        Parameters
        ----------
        operation : Operation
            The operation to execute

        Yields
        ------
        GraphQLResult
            The result of the operation

        """

        raise NotImplementedError("Your Async Transport needs to overwrite this method")


class ContinuationLink(Link):
    """A ContinuationLink is a link that delegates the operation to the next link in the chain.
    It can be either provided a next link or it can be set once the link is composed together
    """

    next: Optional[Link] = None
    """The next link in the chain. This is also set when the link is composed together."""

    def set_next(self, next: Link) -> None:
        """Compose the link with the next link in the chain

        This method is called when the link is composed together with the next link in the chain.
        by the compose helper, this ensures that you cna use the "next" method to delegate the operation
        to the next link in the chain.

        Parameters
        ----------
        next : Link
            The next link in the chain
        """
        self.next = next

    async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
        """Executes an operation against the NEXT link

        This is the main method of the link. It takes an operation and returns an AsyncIterator
        of GraphQLResults. This method should be implemented by subclasses. It is important
        To note that a ContinuationLink should always delegate the operation to the next link
        in the chain. This means that the next link should be called with the same operation.

        Parameters
        ----------
        operation : Operation
            The operation to execute

        Yields
        ------
        GraphQLResult
            The result of the operation

        """
        if not self.next:
            raise NotComposedError("No next link set")

        async for x in self.next.aexecute(operation):
            yield x
