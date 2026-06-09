"""Non-happy-path tests for the HTTP terminating links (aiohttp & httpx).

The aiohttp/httpx links build their own client internally, so most paths require a
live server. The subscription guard needs no network at all, and the httpx response
handling is exercised with a small monkeypatched AsyncClient.
"""
import pytest

import rath.links.httpx as httpx_module
from rath.links.aiohttp import AIOHttpLink
from rath.links.httpx import HttpxLink
from rath.links.errors import MalformedResponseError
from rath.operation import GraphQLException, opify


SUBSCRIPTION = "subscription { newBeast { id } }"
QUERY = "query GetBeast { beast { id } }"


# ---------------------------------------------------------------------------
# subscriptions are not supported over plain HTTP
# ---------------------------------------------------------------------------


async def test_aiohttp_rejects_subscriptions():
    link = AIOHttpLink(endpoint_url="http://example.com/graphql")
    async with link:
        with pytest.raises(NotImplementedError, match="Aiohttp") as excinfo:
            async for _ in link.aexecute(opify(SUBSCRIPTION)):
                pass
    assert "subscription" in str(excinfo.value)


async def test_httpx_rejects_subscriptions():
    link = HttpxLink(endpoint_url="http://example.com/graphql")
    async with link:
        # The message must name the *httpx* transport, not aiohttp.
        with pytest.raises(NotImplementedError, match="Httpx") as excinfo:
            async for _ in link.aexecute(opify(SUBSCRIPTION)):
                pass
    assert "subscription" in str(excinfo.value)


# ---------------------------------------------------------------------------
# httpx response handling (monkeypatched client)
# ---------------------------------------------------------------------------


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class _FakeAsyncClient:
    """Minimal stand-in for httpx.AsyncClient that returns a canned response."""

    _response: _FakeResponse

    async def __aenter__(self) -> "_FakeAsyncClient":
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    async def post(self, url: str, headers=None, **kwargs) -> _FakeResponse:
        return self._response


def _patch_httpx_response(monkeypatch, response: _FakeResponse) -> None:
    client_cls = type("PatchedClient", (_FakeAsyncClient,), {"_response": response})
    monkeypatch.setattr(httpx_module.httpx, "AsyncClient", client_cls)


async def test_httpx_raises_malformed_response_without_data(monkeypatch):
    """A 200 response with neither data nor errors raises MalformedResponseError."""
    _patch_httpx_response(monkeypatch, _FakeResponse(200, {"unexpected": True}))

    link = HttpxLink(endpoint_url="http://example.com/graphql")
    async with link:
        with pytest.raises(MalformedResponseError) as excinfo:
            # No explicit operation_name: the name is derived from the document,
            # which mirrors how callers actually use rath.aquery(...).
            async for _ in link.aexecute(opify(QUERY)):
                pass

    message = str(excinfo.value)
    assert "http://example.com/graphql" in message
    assert "GetBeast" in message  # the operation name is surfaced from the document


async def test_httpx_raises_graphql_exception_with_errors(monkeypatch):
    """GraphQL errors are surfaced as an informative GraphQLException."""
    errors = [{"message": "Field 'beast' not found"}]
    _patch_httpx_response(monkeypatch, _FakeResponse(200, {"errors": errors}))

    link = HttpxLink(endpoint_url="http://example.com/graphql")
    async with link:
        with pytest.raises(GraphQLException) as excinfo:
            async for _ in link.aexecute(opify(QUERY)):
                pass

    exc = excinfo.value
    assert "Field 'beast' not found" in exc.message
    assert exc.endpoint_url == "http://example.com/graphql"
    assert exc.operation is not None
    assert exc.errors == errors
    # The string form surfaces both the endpoint and the (document-derived) op name.
    assert "http://example.com/graphql" in str(exc)
    assert "GetBeast" in str(exc)


async def test_httpx_returns_data_on_success(monkeypatch):
    """Happy-path control through the patched client."""
    _patch_httpx_response(monkeypatch, _FakeResponse(200, {"data": {"beast": {"id": "1"}}}))

    link = HttpxLink(endpoint_url="http://example.com/graphql")
    async with link:
        results = [r async for r in link.aexecute(opify(QUERY))]

    assert results[0].data == {"beast": {"id": "1"}}
