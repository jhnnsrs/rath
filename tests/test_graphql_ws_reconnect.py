"""The subscription link across a reconnect."""

import asyncio

import pytest

from rath.links.graphql_ws import GQL_CONNECTION_ACK, GraphQLWSLink


@pytest.mark.asyncio
async def test_the_acknowledgement_of_a_reconnect_does_not_fail_the_connection() -> (
    None
):
    """Every reconnect is handed the future of the first connection. Resolving it a second
    time raised, which ended each new connection the moment the server acknowledged it."""
    link = GraphQLWSLink(ws_endpoint_url="ws://localhost/graphql")
    connected: asyncio.Future[bool] = asyncio.get_running_loop().create_future()

    await link.broadcast({"type": GQL_CONNECTION_ACK}, connected)
    await link.broadcast({"type": GQL_CONNECTION_ACK}, connected)

    assert connected.result() is True
