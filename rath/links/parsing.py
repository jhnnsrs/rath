from rath.links.base import ContinuationLink
from rath.operation import GraphQLResult, Operation
from typing import AsyncIterator
from rath.errors import NotComposedError


class ParsingLink(ContinuationLink):
    """ParsingLink is a link that parses operation and returns a new operation.
    It is an abstract class that needs to be implemented by the user.
    """

    async def aparse(self, operation: Operation) -> Operation:
        """Parses an operation

        This method needs to be implemented by the user.
        It should parse the operation and return a new operation.

        Parameters
        ----------
        operation : Operation
            The operation to execute

        Returns
        -------
        Operation
            The parsed operation
        """
        raise NotImplementedError("Please implement this method")

    async def aexecute(
        self, operation: Operation, **kwargs
    ) -> AsyncIterator[GraphQLResult]:
        """Executes an operation against the link

        This link will parse the operation and then forward it to the next link,
        the next link will then execute the operation.

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

        operation = await self.aparse(operation)
        async for result in self.next.aexecute(operation, **kwargs):
            yield result
