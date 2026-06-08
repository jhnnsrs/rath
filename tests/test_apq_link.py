"""Tests for ApqLink (Automatic Persisted Queries)."""
import hashlib
import pytest
from typing import AsyncIterator

from rath.links.apq import ApqLink
from rath.links.base import AsyncTerminatingLink
from rath.links import compose
from rath.errors import NotComposedError
from rath.operation import opify, GraphQLException, GraphQLResult, Operation


QUERY = """
query {
    hello
}
"""


def _sha256(text: str) -> str:
    sha256 = hashlib.sha256()
    sha256.update(text.encode("utf-8"))
    return sha256.hexdigest()


def _make_capturing_link():
    received: list[Operation] = []

    class CapturingLink(AsyncTerminatingLink):
        async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
            received.append(operation)
            yield GraphQLResult(data={"hello": "world"})

    return CapturingLink(), received


# ---------------------------------------------------------------------------
# _hash_query
# ---------------------------------------------------------------------------


def test_hash_query_produces_sha256():
    apq = ApqLink()
    query = "query { hello }"
    assert apq._hash_query(query) == _sha256(query)


def test_hash_query_is_deterministic():
    apq = ApqLink()
    query = "query { hello }"
    assert apq._hash_query(query) == apq._hash_query(query)


def test_hash_query_differs_for_different_queries():
    apq = ApqLink()
    assert apq._hash_query("query { a }") != apq._hash_query("query { b }")


# ---------------------------------------------------------------------------
# Normal execution path – extension is set, document is omitted
# ---------------------------------------------------------------------------


async def test_apq_sets_persisted_query_extension():
    """ApqLink stores the persistedQuery extension on context.extensions."""
    terminal, received = _make_capturing_link()
    link = compose(ApqLink(), terminal)

    async with link:
        async for _ in link.aexecute(opify(QUERY)):
            pass

    op = received[0]
    assert "persistedQuery" in op.context.extensions
    pq = op.context.extensions["persistedQuery"]
    assert pq["version"] == 1
    assert pq["sha256Hash"] == _sha256(op.document)


async def test_apq_sets_omit_document_flag():
    """ApqLink sets context.omit_document to True on the first attempt."""
    terminal, received = _make_capturing_link()
    link = compose(ApqLink(), terminal)

    async with link:
        async for _ in link.aexecute(opify(QUERY)):
            pass

    assert received[0].context.omit_document is True


async def test_apq_result_is_forwarded():
    """ApqLink yields the result from the downstream link unchanged."""
    terminal, _ = _make_capturing_link()
    link = compose(ApqLink(), terminal)

    async with link:
        results = [r async for r in link.aexecute(opify(QUERY))]

    assert results == [GraphQLResult(data={"hello": "world"})]


# ---------------------------------------------------------------------------
# PersistedQueryNotFound fallback
# ---------------------------------------------------------------------------


def _make_apq_server_link(not_found_message: str = "PersistedQueryNotFound"):
    """Return a link that rejects the first (hash-only) request with the given
    message, then succeeds on the second (full query) request."""
    state = {"calls": 0, "received": []}

    class ApqServerLink(AsyncTerminatingLink):
        async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
            state["calls"] += 1
            state["received"].append(operation)
            if state["calls"] == 1:
                raise GraphQLException(not_found_message)
            yield GraphQLResult(data={"hello": "from-cache"})

    return ApqServerLink(), state


async def test_apq_retries_with_full_query_on_persisted_query_not_found():
    """ApqLink sends the full query when the server returns PersistedQueryNotFound."""
    terminal, state = _make_apq_server_link("PersistedQueryNotFound")
    link = compose(ApqLink(), terminal)

    async with link:
        results = [r async for r in link.aexecute(opify(QUERY))]

    assert state["calls"] == 2
    assert results == [GraphQLResult(data={"hello": "from-cache"})]


async def test_apq_clears_persisted_query_on_fallback():
    """On fallback the persistedQuery extension is removed from context."""
    terminal, state = _make_apq_server_link("PersistedQueryNotFound")
    link = compose(ApqLink(), terminal)

    async with link:
        async for _ in link.aexecute(opify(QUERY)):
            pass

    # Second call (fallback) should not have persistedQuery in extensions
    second_op: Operation = state["received"][1]
    assert "persistedQuery" not in second_op.context.extensions


async def test_apq_restores_omit_document_on_fallback():
    """On fallback omit_document is reset to False so the query is sent."""
    terminal, state = _make_apq_server_link("PersistedQueryNotFound")
    link = compose(ApqLink(), terminal)

    async with link:
        async for _ in link.aexecute(opify(QUERY)):
            pass

    second_op: Operation = state["received"][1]
    assert second_op.context.omit_document is False


async def test_apq_retries_on_persisted_query_not_found_code():
    """PERSISTED_QUERY_NOT_FOUND (Apollo convention) also triggers the fallback."""
    terminal, state = _make_apq_server_link("PERSISTED_QUERY_NOT_FOUND")
    link = compose(ApqLink(), terminal)

    async with link:
        async for _ in link.aexecute(opify(QUERY)):
            pass

    assert state["calls"] == 2


# ---------------------------------------------------------------------------
# Non-APQ errors are re-raised
# ---------------------------------------------------------------------------


async def test_apq_reraises_unrelated_graphql_exception():
    """Errors unrelated to APQ propagate without triggering the fallback."""
    state = {"calls": 0}

    class AlwaysFailLink(AsyncTerminatingLink):
        async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
            state["calls"] += 1
            raise GraphQLException("some unrelated error")
            yield  # makes this an async generator; never reached

    link = compose(ApqLink(), AlwaysFailLink())
    async with link:
        with pytest.raises(GraphQLException, match="some unrelated error"):
            async for _ in link.aexecute(opify(QUERY)):
                pass

    assert state["calls"] == 1  # no retry


# ---------------------------------------------------------------------------
# Not-composed guard
# ---------------------------------------------------------------------------


async def test_apq_raises_not_composed_error_without_next():
    apq = ApqLink()
    with pytest.raises(NotComposedError):
        async for _ in apq.aexecute(opify(QUERY)):
            pass
