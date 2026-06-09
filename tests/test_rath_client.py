"""Non-happy-path tests for the Rath client itself (link validation, empty results)."""
import pytest
from typing import AsyncIterator

from rath import Rath
from rath.errors import NotConnectedError
from rath.links.base import AsyncTerminatingLink, ContinuationLink
from rath.operation import GraphQLResult, Operation


QUERY = "query { hello }"


class EchoLink(AsyncTerminatingLink):
    """A terminating link that echoes a fixed result."""

    async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
        yield GraphQLResult(data={"hello": "world"})


class EmptyLink(AsyncTerminatingLink):
    """A terminating link that yields nothing (simulates a dead/empty transport)."""

    async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
        return
        yield  # pragma: no cover - makes this an async generator


class PassthroughLink(ContinuationLink):
    """A continuation link that just forwards to its next link."""

    async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
        assert self.next is not None
        async for result in self.next.aexecute(operation):
            yield result


# ---------------------------------------------------------------------------
# link validation
# ---------------------------------------------------------------------------


def test_rath_rejects_non_terminating_link():
    """A bare ContinuationLink is not a valid terminating link for a Rath."""
    with pytest.raises(ValueError, match="TerminatingLink"):
        Rath(link=PassthroughLink())  # type: ignore[arg-type]


def test_rath_rejects_non_link_value():
    """Passing something that is not a link at all is rejected."""
    with pytest.raises(ValueError):
        Rath(link="not-a-link")  # type: ignore[arg-type]


def test_rath_rejects_list_with_non_link_member():
    """A list link chain must contain only links."""
    with pytest.raises(ValueError, match="must be of type Link"):
        Rath(link=[PassthroughLink(), "nope"])  # type: ignore[list-item]


def test_rath_rejects_list_without_terminating_last_link():
    """The last element of a list link chain must be a TerminatingLink."""
    with pytest.raises(ValueError, match="last link"):
        Rath(link=[PassthroughLink(), PassthroughLink()])


def test_rath_accepts_list_link_chain():
    """A valid list link chain is composed into a single terminating link."""
    rath = Rath(link=[PassthroughLink(), EchoLink()])  # type: ignore[arg-type]
    assert rath.link is not None


# ---------------------------------------------------------------------------
# empty result handling
# ---------------------------------------------------------------------------


async def test_aquery_raises_not_connected_when_link_yields_nothing():
    """If the terminating link yields no result, aquery raises NotConnectedError."""
    async with Rath(link=EmptyLink()) as rath:
        with pytest.raises(NotConnectedError, match="Could not retrieve data"):
            await rath.aquery(QUERY)


async def test_aquery_returns_first_result():
    """Happy-path control: a yielding link returns its result."""
    async with Rath(link=EchoLink()) as rath:
        result = await rath.aquery(QUERY)
        assert result.data == {"hello": "world"}
