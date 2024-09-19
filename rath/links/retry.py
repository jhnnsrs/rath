from typing import AsyncIterator, Optional

from rath.links.base import ContinuationLink
from rath.operation import (
    GraphQLException,
    GraphQLResult,
    Operation,
    SubscriptionDisconnect,
)
import logging
import asyncio
from rath.errors import NotComposedError

logger = logging.getLogger(__name__)


class RetryLink(ContinuationLink):
    """RetriyLink is a link that retries a operation  fails.
    This link is stateful, and will keep track of the number of times the
    subscription has been retried."""

    maximum_retry_attempts: int = 3
    """The maximum number of times the operation function will be called, before the operation fails."""
    sleep_interval: Optional[int] = None
    """The number of seconds to wait before retrying the operation."""

    async def aexecute(
        self, operation: Operation, retry: int = 0
    ) -> AsyncIterator[GraphQLResult]:
        """Executes an operation against the link

        This link will retry the operation if it fails.
        It will retry the operation a maximum of maximum_retry_attempts times.
        If a sleep_interval is set, it will wait that many seconds before retrying.

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

        try:
            async for result in self.next.aexecute(operation):
                yield result

        except SubscriptionDisconnect as e:
            if retry > self.maximum_retry_attempts:
                raise GraphQLException(
                    "Maximum refresh attempts reached. Trying to rescribe to"
                ) from e
            if self.sleep_interval:
                await asyncio.sleep(self.sleep_interval)

            logger.info(f"Subscription {operation} disconnected. Retrying {retry}")
            async for result in self.aexecute(operation, retry=retry + 1):
                yield result