from typing import Callable, AsyncIterator

from pydantic import Field
from rath.operation import Operation, GraphQLResult
from rath.links.base import TerminatingLink


class SplitLink(TerminatingLink):
    """SplitLink is a link that splits the operation into two paths. The operation is sent to the left path if the predicate returns true, otherwise to the right path.

    This is useful for exampole when implementing a cache link, where the operation is sent to the cache if it is a query, and to the network if it is a mutation.
    Or when subscriptions and queries are sent to different links (e.g. a websocket link and a http link).
    """

    left: TerminatingLink
    """The link that is used if the predicate returns true."""
    right: TerminatingLink
    """The link that is used if the predicate returns false."""
    split: Callable[[Operation], bool] = Field(exclude=True)
    """The function used to split the operation. This function should return a boolean. If true, the operation is sent to the left path, otherwise to the right path."""

    async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
        """Executes an operation against one of the links
        according to the predicate.

        Parameters
        ----------
        operation : Operation
            The operation to execute, will be to the predicate

        Yields
        ------
        GraphQLResult
            The result of the operation by one of the links
        """

        iterator = (
            self.left.aexecute(operation)
            if self.split(operation)
            else self.right.aexecute(operation)
        )

        async for res in iterator:
            yield res

    async def __aenter__(self) -> None:
        """Enters the context manager of the link"""
        await self.left.__aenter__()
        await self.right.__aenter__()

    async def __aexit__(self, *args, **kwargs) -> None:
        """Exits the context manager of the link"""
        await self.left.__aexit__(*args, **kwargs)
        await self.right.__aexit__(*args, **kwargs)


def split(
    left: TerminatingLink, right: TerminatingLink, split: Callable[[Operation], bool]
) -> SplitLink:
    """
    Splits a Link into two paths. Acording to a predicate function. If predicate returns
    true, the operation is sent to the left path, otherwise to the right path.

    Parameters
    ----------
    left : TerminatingLink
        The link that is used if the predicate returns true.
    right : TerminatingLink
        The link that is used if the predicate returns false.
    split : Callable[[Operation], bool]
        The function used to split the operation. This function should return a boolean. If true,
        the operation is sent to the left path, otherwise to the right path.

    Returns
    -------
    SplitLink
        The split link that splits the operation according to the predicate.
    """
    return SplitLink(left=left, right=right, split=split)
