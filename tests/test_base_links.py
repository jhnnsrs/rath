"""Tests for Link, ContinuationLink, ComposedLink and the compose() helper."""
import pytest
from typing import AsyncIterator

from rath.links.base import AsyncTerminatingLink, ContinuationLink, Link
from rath.links import compose
from rath.links.compose import ComposedLink
from rath.errors import NotComposedError
from rath.operation import opify, GraphQLResult, Operation


QUERY = """
query {
    hello
}
"""


# ---------------------------------------------------------------------------
# Simple terminating link fixtures
# ---------------------------------------------------------------------------


class EchoLink(AsyncTerminatingLink):
    """Returns a fixed result."""

    async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
        yield GraphQLResult(data={"echo": operation.document})


class CountingLink(AsyncTerminatingLink):
    """Counts how many times it is executed."""

    call_count: int = 0

    async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
        # mutate the underlying int via object state workaround
        object.__setattr__(self, "call_count", self.call_count + 1)
        yield GraphQLResult(data={"count": self.call_count})


# ---------------------------------------------------------------------------
# Base Link – context manager
# ---------------------------------------------------------------------------


async def test_link_context_manager_enters_and_exits():
    """Link.__aenter__ returns self and __aexit__ does not raise."""
    link = EchoLink()
    async with link as entered:
        assert entered is link


async def test_link_aconnect_and_adisconnect_are_noops():
    """Default aconnect / adisconnect are no-ops (do not raise)."""
    link = EchoLink()
    op = opify(QUERY)
    await link.aconnect(op)
    await link.adisconnect()


# ---------------------------------------------------------------------------
# ContinuationLink – set_next and delegation
# ---------------------------------------------------------------------------


class PassthroughLink(ContinuationLink):
    """Delegates to next without modification."""

    async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
        if not self.next:
            raise NotComposedError("No next link set")
        async for result in self.next.aexecute(operation):
            yield result


async def test_continuation_link_delegates_to_next():
    """ContinuationLink forwards the operation to the next link."""
    terminal = EchoLink()
    continuation = PassthroughLink()
    continuation.set_next(terminal)

    results = [r async for r in continuation.aexecute(opify(QUERY))]
    assert len(results) == 1
    assert "echo" in results[0].data


async def test_continuation_link_raises_without_next():
    """ContinuationLink raises NotComposedError when next is not set."""
    link = PassthroughLink()
    with pytest.raises(NotComposedError):
        async for _ in link.aexecute(opify(QUERY)):
            pass


async def test_base_continuation_link_raises_without_next():
    """The base ContinuationLink.aexecute also raises NotComposedError."""
    link = ContinuationLink()
    with pytest.raises(NotComposedError):
        async for _ in link.aexecute(opify(QUERY)):
            pass


async def test_set_next_stores_next_link():
    link = PassthroughLink()
    terminal = EchoLink()
    link.set_next(terminal)
    assert link.next is terminal


# ---------------------------------------------------------------------------
# compose() – function
# ---------------------------------------------------------------------------


async def test_compose_single_terminating_link():
    """compose() accepts a single TerminatingLink."""
    composed = compose(EchoLink())
    async with composed:
        results = [r async for r in composed.aexecute(opify(QUERY))]
    assert len(results) == 1


async def test_compose_continuation_plus_terminating():
    """compose() wires two links and executes end-to-end."""
    composed = compose(PassthroughLink(), EchoLink())
    async with composed:
        results = [r async for r in composed.aexecute(opify(QUERY))]
    assert results[0].data["echo"]


async def test_compose_sets_next_on_enter():
    """Links do not have next set until the composed chain is entered."""
    passthrough = PassthroughLink()
    echo = EchoLink()
    composed = compose(passthrough, echo)

    assert passthrough.next is None  # before entering

    async with composed:
        assert passthrough.next is echo  # set during __aenter__


async def test_compose_multiple_continuation_links():
    """compose() supports more than two links in the chain."""

    class HeaderInjectingLink(ContinuationLink):
        async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
            operation.context.headers["X-Test"] = "injected"
            async for r in self.next.aexecute(operation):
                yield r

    received: list[Operation] = []

    class CapturingTerminal(AsyncTerminatingLink):
        async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
            received.append(operation)
            yield GraphQLResult(data={})

    composed = compose(
        PassthroughLink(),
        HeaderInjectingLink(),
        CapturingTerminal(),
    )
    async with composed:
        async for _ in composed.aexecute(opify(QUERY)):
            pass

    assert received[0].context.headers["X-Test"] == "injected"


# ---------------------------------------------------------------------------
# ComposedLink – validation
# ---------------------------------------------------------------------------


def test_compose_requires_terminating_last_link():
    """ComposedLink refuses a chain whose last link is a ContinuationLink."""
    with pytest.raises(Exception):
        compose(PassthroughLink(), PassthroughLink())


def test_compose_refuses_empty_links():
    """ComposedLink refuses an empty links list."""
    with pytest.raises(Exception):
        ComposedLink(links=[])


def test_compose_refuses_terminating_link_in_middle():
    """ComposedLink refuses a TerminatingLink that is not the last link."""
    with pytest.raises(Exception):
        compose(EchoLink(), EchoLink())


# ---------------------------------------------------------------------------
# ComposedLink – lifecycle
# ---------------------------------------------------------------------------


async def test_composed_link_enters_and_exits_cleanly():
    """ComposedLink context manager enters and exits without error."""
    composed = compose(PassthroughLink(), EchoLink())
    async with composed:
        pass  # just entering and exiting should be fine


async def test_composed_link_can_be_entered_multiple_times():
    """A ComposedLink can be re-entered after exit."""
    composed = compose(EchoLink())
    async with composed:
        r1 = [r async for r in composed.aexecute(opify(QUERY))]
    async with composed:
        r2 = [r async for r in composed.aexecute(opify(QUERY))]

    assert r1[0].data == r2[0].data
