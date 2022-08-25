from typing import AsyncIterator, Awaitable, Callable, Optional

from pydantic import Field
from rath.links.base import ContinuationLink
from rath.operation import (
    GraphQLException,
    GraphQLResult,
    Operation,
    SubscriptionDisconnect,
)
from rath.links.errors import AuthenticationError
import logging


logger = logging.getLogger(__name__)


class SubscriptionRetry(ContinuationLink):
    maximum_retry_attempts = 3

    async def aexecute(
        self, operation: Operation, retry=0, **kwargs
    ) -> AsyncIterator[GraphQLResult]:

        try:

            async for result in self.next.aexecute(operation, **kwargs):
                yield result

        except SubscriptionDisconnect as e:
            if retry > self.maximum_retry_attempts:
                raise GraphQLException(
                    "Maximum refresh attempts reached. Trying to rescribe to"
                ) from e

            logger.info(f"Subscription {operation} disconnected. Retrying {retry}")
            async for result in self.aexecute(operation, retry=retry + 1, **kwargs):
                yield result

    class Config:
        underscore_attrs_are_private = True
        arbitary_types_allowed = True
