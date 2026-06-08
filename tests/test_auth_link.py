"""Tests for AuthTokenLink and ComposedAuthLink."""
import pytest
from typing import AsyncIterator

from rath.links.auth import AuthTokenLink, ComposedAuthLink
from rath.links.base import AsyncTerminatingLink
from rath.links.errors import AuthenticationError
from rath.links import compose
from rath.errors import NotComposedError
from rath.operation import opify, GraphQLResult, Operation


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

QUERY = """
query {
    hello
}
"""


def _make_capturing_link():
    """Return (link, list) where every received operation is appended to the list."""
    received: list[Operation] = []

    class CapturingLink(AsyncTerminatingLink):
        async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
            received.append(operation)
            yield GraphQLResult(data={"hello": "world"})

    return CapturingLink(), received


def _make_failing_then_succeeding_link(fail_times: int = 1):
    """Return a terminating link that raises AuthenticationError for the first
    *fail_times* calls, then succeeds."""
    state = {"calls": 0}

    class ConditionalLink(AsyncTerminatingLink):
        async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
            state["calls"] += 1
            if state["calls"] <= fail_times:
                raise AuthenticationError("Token expired")
            yield GraphQLResult(data={"hello": "ok"})

    return ConditionalLink(), state


# ---------------------------------------------------------------------------
# AuthTokenLink – happy path
# ---------------------------------------------------------------------------


async def test_auth_sets_authorization_header():
    """AuthTokenLink injects a Bearer token into context.headers."""
    terminal, received = _make_capturing_link()

    class SimpleAuth(AuthTokenLink):
        async def aload_token(self, operation: Operation) -> str:
            return "my-token"

    link = compose(SimpleAuth(), terminal)
    async with link:
        async for _ in link.aexecute(opify(QUERY)):
            pass

    assert len(received) == 1
    assert received[0].context.headers["Authorization"] == "Bearer my-token"


async def test_auth_sets_initial_payload_token():
    """AuthTokenLink puts the token in context.initial_payload as well."""
    terminal, received = _make_capturing_link()

    class SimpleAuth(AuthTokenLink):
        async def aload_token(self, operation: Operation) -> str:
            return "payload-token"

    link = compose(SimpleAuth(), terminal)
    async with link:
        async for _ in link.aexecute(opify(QUERY)):
            pass

    assert received[0].context.initial_payload["token"] == "payload-token"


async def test_auth_result_is_forwarded():
    """AuthTokenLink yields the downstream result unchanged."""
    terminal, _ = _make_capturing_link()

    class SimpleAuth(AuthTokenLink):
        async def aload_token(self, operation: Operation) -> str:
            return "tok"

    link = compose(SimpleAuth(), terminal)
    async with link:
        results = [r async for r in link.aexecute(opify(QUERY))]

    assert results == [GraphQLResult(data={"hello": "world"})]


# ---------------------------------------------------------------------------
# AuthTokenLink – retry / refresh
# ---------------------------------------------------------------------------


async def test_auth_refreshes_token_on_authentication_error():
    """AuthTokenLink calls arefresh_token exactly once when downstream raises."""
    terminal, state = _make_failing_then_succeeding_link(fail_times=1)
    refresh_calls: list[str] = []

    class TrackingAuth(AuthTokenLink):
        async def aload_token(self, operation: Operation) -> str:
            return "initial"

        async def arefresh_token(self, operation: Operation) -> str:
            refresh_calls.append("refresh")
            return "refreshed"

    link = compose(TrackingAuth(), terminal)
    async with link:
        results = [r async for r in link.aexecute(opify(QUERY))]

    assert len(refresh_calls) == 1
    assert results[0].data == {"hello": "ok"}


async def test_auth_raises_after_max_refresh_attempts():
    """AuthTokenLink raises AuthenticationError when max attempts are exhausted."""
    # Always fails → triggers maximum_refresh_attempts exceeded
    terminal, _ = _make_failing_then_succeeding_link(fail_times=999)

    class AlwaysFailAuth(AuthTokenLink):
        maximum_refresh_attempts: int = 2

        async def aload_token(self, operation: Operation) -> str:
            return "token"

        async def arefresh_token(self, operation: Operation) -> str:
            return "new-token"

    link = compose(AlwaysFailAuth(), terminal)
    async with link:
        with pytest.raises(AuthenticationError):
            async for _ in link.aexecute(opify(QUERY)):
                pass


async def test_auth_no_refresh_called_on_success():
    """arefresh_token is never called when the downstream link succeeds."""
    terminal, _ = _make_capturing_link()
    refresh_calls: list[str] = []

    class TrackingAuth(AuthTokenLink):
        async def aload_token(self, operation: Operation) -> str:
            return "good"

        async def arefresh_token(self, operation: Operation) -> str:
            refresh_calls.append("should-not-happen")
            return "refreshed"

    link = compose(TrackingAuth(), terminal)
    async with link:
        async for _ in link.aexecute(opify(QUERY)):
            pass

    assert refresh_calls == []


# ---------------------------------------------------------------------------
# AuthTokenLink – not-composed guard
# ---------------------------------------------------------------------------


async def test_auth_raises_not_composed_error_without_next():
    """Calling aexecute with no next link set raises NotComposedError."""

    class SimpleAuth(AuthTokenLink):
        async def aload_token(self, operation: Operation) -> str:
            return "tok"

    auth = SimpleAuth()
    with pytest.raises(NotComposedError):
        async for _ in auth.aexecute(opify(QUERY)):
            pass


# ---------------------------------------------------------------------------
# ComposedAuthLink
# ---------------------------------------------------------------------------


async def test_composed_auth_link_uses_token_loader():
    """ComposedAuthLink delegates to the provided token_loader callable."""
    terminal, received = _make_capturing_link()
    calls: list[str] = []

    async def loader() -> str:
        calls.append("load")
        return "functional-token"

    link = compose(ComposedAuthLink(token_loader=loader), terminal)
    async with link:
        async for _ in link.aexecute(opify(QUERY)):
            pass

    assert calls == ["load"]
    assert received[0].context.headers["Authorization"] == "Bearer functional-token"


async def test_composed_auth_link_uses_token_refresher():
    """ComposedAuthLink calls the token_refresher on AuthenticationError."""
    terminal, state = _make_failing_then_succeeding_link(fail_times=1)
    refreshed: list[str] = []

    async def loader() -> str:
        return "initial"

    async def refresher() -> str:
        refreshed.append("refreshed")
        return "new"

    link = compose(
        ComposedAuthLink(token_loader=loader, token_refresher=refresher), terminal
    )
    async with link:
        async for _ in link.aexecute(opify(QUERY)):
            pass

    assert refreshed == ["refreshed"]


async def test_composed_auth_raises_without_loader():
    """ComposedAuthLink raises when token_loader is None."""
    terminal, _ = _make_capturing_link()
    link = compose(ComposedAuthLink(token_loader=None), terminal)

    async with link:
        with pytest.raises(Exception, match="No Token loader specified"):
            async for _ in link.aexecute(opify(QUERY)):
                pass


async def test_composed_auth_raises_without_refresher_on_auth_error():
    """ComposedAuthLink raises when token_refresher is None and auth fails."""
    terminal, _ = _make_failing_then_succeeding_link(fail_times=999)

    async def loader() -> str:
        return "initial"

    link = compose(
        ComposedAuthLink(token_loader=loader, token_refresher=None), terminal
    )

    async with link:
        with pytest.raises(Exception):
            async for _ in link.aexecute(opify(QUERY)):
                pass
