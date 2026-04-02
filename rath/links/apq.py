from typing import AsyncIterator, Awaitable, Callable, Optional

from graphql import GraphQLError, GraphQLErrorExtensions

from rath.links.base import ContinuationLink
from rath.operation import GraphQLException, GraphQLResult, Operation
from rath.links.errors import AuthenticationError
from rath.errors import NotComposedError


class ApqLink(ContinuationLink):
    """A link that implements the Automatic Persisted Queries (APQ) protocol.
    This link will attempt to send only the hash of the query on the first request. If the server responds with an error indicating that the query is not found,
    the link will resend the full query along with the hash.
    """

    maximum_refresh_attempts: int = 3
    """The maximum number of times the token_refresher function will be called, before the operation fails."""

    load_token_on_connect: bool = True
    """If True, the token_loader function will be called when the link is connected."""
    load_token_on_enter: bool = True
    """If True, the token_loader function will be called when the link is entered."""

    async def aload_token(self, operation: Operation) -> str:
        """A function that loads the authentication token.

        This function should return a string containing the authentication token.

        Parameters
        ----------
        operation : Operation
            The operation to execute

        Raises
        ------
        Exception
            When the token cannot be loaded
        """
        raise Exception("No Token loader specified")

    def _hash_query(self, query: str) -> str:
        """Computes a SHA-256 hash of the given query string.

        Parameters
        ----------
        query : str
            The GraphQL query string to hash.

        Returns
        -------
        str
            The hexadecimal representation of the SHA-256 hash.
        """
        import hashlib

        sha256 = hashlib.sha256()
        sha256.update(query.encode("utf-8"))
        return sha256.hexdigest()

    async def arefresh_token(self, operation: Operation) -> str:
        """A function that refreshes the authentication token.

        This function should return a string containing the authentication token.
        In comparison to the token_loader function, this function is called when
        the server already raised an AuthenticationError, so a refresh should really
        be attempted.

        Parameters
        ----------
        operation : Operation
            The operation to execute

        Raises
        ------
        Exception
            When the token cannot be refreshed
        """
        raise Exception("No Token refresher specified")

    async def aexecute(
        self, operation: Operation, retry: int = 0
    ) -> AsyncIterator[GraphQLResult]:
        """Executes and forwards an operation to the next link.

        This method will add the authentication token to the context of the operation,
        and will refresh the token if the next link raises an AuthenticationError, until
        the maximum number of refresh attempts is reached.

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

        operation.context.extensions["persistedQuery"] = {
            "version": 1,
            "sha256Hash": self._hash_query(operation.query),
        }
        operation.context.omit_document = True

        try:
            async for result in self.next.aexecute(operation):
                yield result

        except GraphQLException as e:
            is_persiting_error = False
            for e in e.errors:
                if (
                    e.errors.get("message") == "PersistedQueryNotFound"
                    or e.errors.get("code") == "PERSISTED_QUERY_NOT_FOUND"
                ):
                    is_persiting_error = True

            if is_persiting_error:
                # Resend the operation with the full query
                operation.context.extensions.pop("persistedQuery", None)
                async for result in self.next.aexecute(operation):
                    yield result
            else:
                raise e
