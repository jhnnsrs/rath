import hashlib
from typing import AsyncIterator

from rath.links.base import ContinuationLink
from rath.operation import GraphQLException, GraphQLResult, Operation
from rath.errors import NotComposedError


class ApqLink(ContinuationLink):
    """A link that implements the Automatic Persisted Queries (APQ) protocol.

    On the first request only the SHA-256 hash of the query is sent.  If the
    server responds with a "PersistedQueryNotFound" error the full query is
    resent together with the hash so the server can cache it for next time.
    """

    def _hash_query(self, query: str) -> str:
        sha256 = hashlib.sha256()
        sha256.update(query.encode("utf-8"))
        return sha256.hexdigest()

    async def aexecute(
        self, operation: Operation
    ) -> AsyncIterator[GraphQLResult]:
        if not self.next:
            raise NotComposedError("No next link set")

        operation.context.extensions["persistedQuery"] = {
            "version": 1,
            "sha256Hash": self._hash_query(operation.document),
        }
        operation.context.omit_document = True

        try:
            async for result in self.next.aexecute(operation):
                yield result

        except GraphQLException as exc:
            is_persisted_query_error = (
                "PersistedQueryNotFound" in exc.message
                or "PERSISTED_QUERY_NOT_FOUND" in exc.message
            )

            if is_persisted_query_error:
                operation.context.extensions.pop("persistedQuery", None)
                operation.context.omit_document = False
                async for result in self.next.aexecute(operation):
                    yield result
            else:
                raise exc
