"""Tests for routing the terminating links through an HTTP forward proxy.

A tiny asyncio TCP server stands in for the mesh sidecar's forward proxy. It records
the request line it receives: an absolute-form request line for plain http, and a
``CONNECT host:port`` line for websockets.
"""
import asyncio
import json
from typing import AsyncIterator, List, Tuple

import pytest

from rath.links import websocket_connect
from rath.links.aiohttp import AIOHttpLink
from rath.links.graphql_ws import GraphQLWSLink
from rath.links.httpx import HttpxLink
from rath.operation import opify

QUERY = "query GetBeast { beast { id } }"
SUBSCRIPTION = "subscription { newBeast { id } }"
RESPONSE = json.dumps({"data": {"beast": {"id": "1"}}}).encode()


class RecordingServer:
    """Records request lines and answers every plain request with a GraphQL result.

    CONNECT requests are recorded and refused with a 403, which is enough to prove
    the client tried to tunnel through the proxy.
    """

    def __init__(self) -> None:
        self.request_lines: List[str] = []
        self.connect_seen = asyncio.Event()
        self.server: asyncio.AbstractServer | None = None

    @property
    def url(self) -> str:
        assert self.server
        host, port = self.server.sockets[0].getsockname()[:2]
        return f"http://{host}:{port}"

    async def handle(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            request_line = (await reader.readline()).decode().rstrip("\r\n")
            self.request_lines.append(request_line)
            content_length = 0
            while True:
                line = await reader.readline()
                if line in (b"\r\n", b"\n", b""):
                    break
                name, _, value = line.decode().partition(":")
                if name.strip().lower() == "content-length":
                    content_length = int(value.strip())
            if content_length:
                await reader.readexactly(content_length)

            if request_line.startswith("CONNECT "):
                self.connect_seen.set()
                writer.write(b"HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")
            else:
                writer.write(
                    b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
                    + f"Content-Length: {len(RESPONSE)}\r\n".encode()
                    + b"Connection: close\r\n\r\n"
                    + RESPONSE
                )
            await writer.drain()
        finally:
            writer.close()


@pytest.fixture
async def recording_server() -> AsyncIterator[RecordingServer]:
    recorder = RecordingServer()
    recorder.server = await asyncio.start_server(recorder.handle, "127.0.0.1", 0)
    try:
        yield recorder
    finally:
        recorder.server.close()
        await recorder.server.wait_closed()


async def _execute(link) -> Tuple[dict, ...]:
    async with link:
        return tuple([result.data async for result in link.aexecute(opify(QUERY))])


async def test_aiohttp_routes_through_proxy(recording_server: RecordingServer):
    """With a proxy set, aiohttp sends an absolute-form request to the proxy.

    ``example.mesh`` does not resolve, so the request can only succeed via the proxy.
    """
    link = AIOHttpLink(endpoint_url="http://example.mesh:8080/graphql", proxy=recording_server.url)
    results = await _execute(link)

    assert results == ({"beast": {"id": "1"}},)
    assert recording_server.request_lines == ["POST http://example.mesh:8080/graphql HTTP/1.1"]


async def test_aiohttp_without_proxy_goes_direct(recording_server: RecordingServer):
    """Without a proxy, aiohttp talks to the endpoint directly (origin-form)."""
    link = AIOHttpLink(endpoint_url=f"{recording_server.url}/graphql")
    assert link.proxy is None
    results = await _execute(link)

    assert results == ({"beast": {"id": "1"}},)
    assert recording_server.request_lines == ["POST /graphql HTTP/1.1"]


async def test_httpx_routes_through_proxy(recording_server: RecordingServer):
    """With a proxy set, httpx sends an absolute-form request to the proxy."""
    link = HttpxLink(endpoint_url="http://example.mesh:8080/graphql", proxy=recording_server.url)
    results = await _execute(link)

    assert results == ({"beast": {"id": "1"}},)
    assert recording_server.request_lines == ["POST http://example.mesh:8080/graphql HTTP/1.1"]


async def test_httpx_without_proxy_goes_direct(recording_server: RecordingServer):
    """Without a proxy, httpx talks to the endpoint directly (origin-form)."""
    link = HttpxLink(endpoint_url=f"{recording_server.url}/graphql")
    results = await _execute(link)

    assert results == ({"beast": {"id": "1"}},)
    assert recording_server.request_lines == ["POST /graphql HTTP/1.1"]


@pytest.mark.skipif(not websocket_connect.SUPPORTS_PROXY, reason="websocket proxies need websockets>=15")
async def test_graphql_ws_tunnels_through_proxy(recording_server: RecordingServer):
    """With a proxy set, the websocket link issues ``CONNECT host:port`` to the proxy."""
    link = GraphQLWSLink(
        ws_endpoint_url="ws://example.mesh:8080/graphql",
        proxy=recording_server.url,
        allow_reconnect=False,
        max_retries=0,
        time_between_retries=0,
    )

    async def consume() -> None:
        async with link:
            async for _ in link.aexecute(opify(SUBSCRIPTION)):
                pass

    task = asyncio.create_task(consume())
    try:
        await asyncio.wait_for(recording_server.connect_seen.wait(), timeout=5)
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)

    assert recording_server.request_lines[0] == "CONNECT example.mesh:8080 HTTP/1.1"


@pytest.mark.skipif(websocket_connect.SUPPORTS_PROXY, reason="only relevant for websockets without proxy support")
def test_ws_proxy_on_old_websockets_raises():
    """On a websockets without proxy support, asking for a proxy fails loudly."""
    with pytest.raises(RuntimeError, match="websockets>=15"):
        websocket_connect.ws_connect("ws://example.mesh/graphql", ["graphql-transport-ws"], None, proxy="http://127.0.0.1:1")


async def _pipe(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        while data := await reader.read(65536):
            writer.write(data)
            await writer.drain()
    finally:
        writer.close()


@pytest.mark.skipif(not websocket_connect.SUPPORTS_PROXY, reason="websocket proxies need websockets>=15")
async def test_graphql_ws_subscription_through_tunnel():
    """A full subscription round trip through a CONNECT tunnel to a local ws server."""
    from websockets.asyncio.server import serve

    async def ws_handler(ws) -> None:
        async for raw in ws:
            message = json.loads(raw)
            if message["type"] == "connection_init":
                await ws.send(json.dumps({"type": "connection_ack"}))
            elif message["type"] == "start":
                await ws.send(json.dumps({"type": "data", "id": message["id"], "payload": {"data": {"newBeast": {"id": "1"}}}}))
                await ws.send(json.dumps({"type": "complete", "id": message["id"]}))

    connect_lines: List[str] = []

    async def tunnel(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        connect_lines.append((await reader.readline()).decode().rstrip("\r\n"))
        while (await reader.readline()) not in (b"\r\n", b"\n", b""):
            pass
        up_reader, up_writer = await asyncio.open_connection("127.0.0.1", ws_port)
        writer.write(b"HTTP/1.1 200 Connection established\r\n\r\n")
        await writer.drain()
        await asyncio.gather(_pipe(reader, up_writer), _pipe(up_reader, writer), return_exceptions=True)

    async with serve(ws_handler, "127.0.0.1", 0, subprotocols=["graphql-ws"]) as ws_server:
        ws_port = ws_server.sockets[0].getsockname()[1]
        proxy = await asyncio.start_server(tunnel, "127.0.0.1", 0)
        proxy_port = proxy.sockets[0].getsockname()[1]
        try:
            link = GraphQLWSLink(ws_endpoint_url="ws://example.mesh:8080/graphql", proxy=f"http://127.0.0.1:{proxy_port}", allow_reconnect=False)

            async def run() -> List[dict]:
                async with link:
                    return [r.data async for r in link.aexecute(opify(SUBSCRIPTION))]

            results = await asyncio.wait_for(run(), timeout=5)
        finally:
            proxy.close()

    assert results == [{"newBeast": {"id": "1"}}]
    assert connect_lines == ["CONNECT example.mesh:8080 HTTP/1.1"]


@pytest.mark.skipif(not websocket_connect.SUPPORTS_PROXY, reason="websockets < 15 never reads proxy variables")
async def test_graphql_ws_ignores_socks_proxy_variables(monkeypatch: pytest.MonkeyPatch):
    """Without a proxy the link connects directly, even with ALL_PROXY=socks5h
    exported for some other tool (websockets would otherwise need python-socks
    and route through it)."""
    from websockets.asyncio.server import serve

    async def ws_handler(ws) -> None:
        async for raw in ws:
            message = json.loads(raw)
            if message["type"] == "connection_init":
                await ws.send(json.dumps({"type": "connection_ack"}))
            elif message["type"] == "start":
                await ws.send(json.dumps({"type": "data", "id": message["id"], "payload": {"data": {"newBeast": {"id": "1"}}}}))
                await ws.send(json.dumps({"type": "complete", "id": message["id"]}))

    for var in ("ALL_PROXY", "all_proxy", "HTTP_PROXY", "http_proxy", "SOCKS_PROXY"):
        monkeypatch.setenv(var, "socks5h://127.0.0.1:1")
    async with serve(ws_handler, "127.0.0.1", 0, subprotocols=["graphql-ws"]) as ws_server:
        port = ws_server.sockets[0].getsockname()[1]
        link = GraphQLWSLink(ws_endpoint_url=f"ws://127.0.0.1:{port}/graphql", allow_reconnect=False)

        async def run() -> List[dict]:
            async with link:
                return [r.data async for r in link.aexecute(opify(SUBSCRIPTION))]

        assert await asyncio.wait_for(run(), timeout=5) == [{"newBeast": {"id": "1"}}]
