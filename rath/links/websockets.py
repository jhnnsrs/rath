from ssl import SSLContext
from typing import Awaitable, Callable, Dict, Optional
from graphql import OperationType
from pydantic import Field
import websockets
import json
import asyncio
from websockets.exceptions import (
    ConnectionClosedError,
)
import logging
import uuid
import ssl
import certifi
from rath.links.errors import LinkNotConnectedError, TerminatingLinkError

from rath.operation import (
    GraphQLException,
    GraphQLResult,
    Operation,
    SubscriptionDisconnect,
)
from rath.links.base import AsyncTerminatingLink


logger = logging.getLogger(__name__)


GQL_WS_SUBPROTOCOL = "graphql-ws"

# all the message types
GQL_CONNECTION_INIT = "connection_init"
GQL_START = "start"
GQL_STOP = "stop"
GQL_CONNECTION_TERMINATE = "connection_terminate"
GQL_CONNECTION_ERROR = "connection_error"
GQL_CONNECTION_ACK = "connection_ack"
GQL_DATA = "data"
GQL_ERROR = "error"
GQL_COMPLETE = "complete"
GQL_CONNECTION_KEEP_ALIVE = "ka"

WEBSOCKET_DEAD = "websocket_dead"
WEBSOCKET_CANCELLED = "websocket_cancelled"


class CorrectableConnectionFail(TerminatingLinkError):
    pass


class DefiniteConnectionFail(TerminatingLinkError):
    pass


class InvalidPayload(TerminatingLinkError):
    pass


async def none_token_loader():
    raise Exception("Token loader was not set")


class WebSocketLink(AsyncTerminatingLink):
    """WebSocketLink is a terminating link that sends operations over websockets using websockets

    This is a terminating link, so it should be the last link in the chain.
    This is a stateful link, keeing a connection open and sending messages over it.

    """

    ws_endpoint_url: str
    """ The endpoint url to connect to """
    allow_reconnect: bool = True
    """ Should the websocket try to reconnect if it fails """
    time_between_retries = 4
    """ The sleep time between retries """
    max_retries = 3
    """ The maximum amount of retries before giving up """
    ssl_context: SSLContext = Field(
        default_factory=lambda: ssl.create_default_context(cafile=certifi.where())
    )
    """ The SSL Context to use for the connection """
    token_loader: Callable[[], Awaitable[str]] = Field(
        default_factory=lambda: none_token_loader, exclude=True
    )
    """ A function that returns the token to use for the connection as a query parameter """


    _connected: bool = False
    _alive: bool = False
    _send_queue: asyncio.Queue = None
    _connection_task: asyncio.Task = None
    _ongoing_subscriptions: Optional[Dict[str, asyncio.Queue]] = None

    async def aforward(self, message):
        await self._send_queue.put(message)

    async def __aenter__(self):
        self._ongoing_subscriptions = {}
        self._send_queue = asyncio.Queue()

    async def aconnect(self):
        logger.info("Connecting Websockets")
        self._connection_task = asyncio.create_task(self.websocket_loop())
        self._connected = True

    async def adisconnect(self):
        self._connection_task.cancel()

        try:
            await self._connection_task
        except asyncio.CancelledError:
            logger.info(f"Websocket Transport {self} succesfully disconnected")

    async def __aexit__(self, *args, **kwargs):
        if self._connection_task:
            await self.adisconnect()

    async def websocket_loop(self, retry=0):
        send_task = None
        receive_task = None
        try:
            try:
                token = await self.token_loader()
                url = (
                    f"{self.ws_endpoint_url}?token={token}"
                    if token
                    else self.ws_endpoint_url
                )
                async with websockets.connect(
                    url,
                    subprotocols=[GQL_WS_SUBPROTOCOL],
                    ssl=self.ssl_context if url.startswith("wss") else None,
                ) as client:
                    logger.info("Websocket successfully connected")

                    send_task = asyncio.create_task(self.sending(client))
                    receive_task = asyncio.create_task(self.receiving(client))

                    self._alive = True
                    done, pending = await asyncio.wait(
                        [send_task, receive_task],
                        return_when=asyncio.FIRST_EXCEPTION,
                    )
                    self._alive = False

                    for task in pending:
                        task.cancel()

                    for task in done:
                        raise task.exception()

            except Exception as e:
                logger.warning("Websocket excepted. Trying to recover", exc_info=True)
                raise CorrectableConnectionFail from e

        except CorrectableConnectionFail as e:
            logger.info(
                f"Trying to Recover from Exception {e} Reconnect is {self.allow_reconnect} Retry: {retry}"
            )
            if retry > self.max_retries or not self.allow_reconnect:
                logger.error("Max retries reached. Aborting")
                raise DefiniteConnectionFail("Exceeded Number of Retries")

            await asyncio.sleep(self.time_between_retries)
            logger.info(f"Retrying to connect")
            await self.broadcast({"type": WEBSOCKET_DEAD, "error": e})
            await self.websocket_loop(retry=retry + 1)

        except DefiniteConnectionFail as e:
            logger.error("Websocket excepted closed definetely", exc_info=True)
            self.connection_dead = True
            raise e

        except asyncio.CancelledError as e:
            logger.info("Websocket got cancelled. Trying to shutdown graceully")
            if send_task and receive_task:
                send_task.cancel()
                receive_task.cancel()

                cancellation = await asyncio.gather(
                    send_task, receive_task, return_exceptions=True
                )
            raise e

        except Exception as e:
            logger.error("Websocket excepted", exc_info=True)
            self.connection_dead = True
            raise e

    async def sending(self, client, headers=None):
        payload = {"type": GQL_CONNECTION_INIT, "payload": {"headers": headers}}
        await client.send(json.dumps(payload))

        try:
            while True:
                message = await self._send_queue.get()
                logger.debug("GraphQL Websocket: >>>>>> " + message)
                await client.send(message)
                self._send_queue.task_done()
        except asyncio.CancelledError as e:
            logger.debug("Sending Task sucessfully Cancelled")  #
            raise e

    async def receiving(self, client):
        try:
            async for message in client:
                logger.debug("GraphQL Websocket: <<<<<<< " + message)
                try:
                    message = json.loads(message)
                    await self.broadcast(message)
                except json.JSONDecodeError as err:
                    logger.warning(
                        "Ignoring. Server sent invalid JSON data: %s \n %s",
                        message,
                        err,
                    )
        except Exception as e:
            logger.warning("Websocket excepted. Trying to recover", exc_info=True)
            raise e

    async def broadcast(self, message: dict):
        type = message["type"]

        if type == GQL_CONNECTION_KEEP_ALIVE:
            return

        if type == GQL_CONNECTION_KEEP_ALIVE:
            return

        if type == WEBSOCKET_DEAD:
            # notify all subscriptipns that the websocket is dead
            for subscription in self._ongoing_subscriptions.values():
                await subscription.put(message)
            return

        if type in [GQL_DATA, GQL_COMPLETE]:

            if "id" not in message:
                raise InvalidPayload(f"Protocol Violation. Expected 'id' in {message}")

            id = message["id"]
            assert (
                id in self._ongoing_subscriptions
            ), "Received Result for subscription that is no longer or was never active"
            await self._ongoing_subscriptions[id].put(message)

    async def aexecute(self, operation: Operation):
        if self._connection_task == False:
            raise LinkNotConnectedError("Websocket_link is not connected")

        assert (
            operation.node.operation == OperationType.SUBSCRIPTION
        ), "Operation is not a subscription"
        assert not operation.context.files, "We cannot send files through websockets"

        id = operation.id
        subscribe_queue = asyncio.Queue()
        self._ongoing_subscriptions[id] = subscribe_queue

        payload = {
            "headers": operation.context.headers,
            "query": operation.document,
            "variables": operation.variables,
        }
        frame = {"id": id, "type": GQL_START, "payload": payload}
        await self.aforward(json.dumps(frame))

        while True:
            answer = await subscribe_queue.get()

            if answer["type"] == GQL_DATA:
                payload = answer["payload"]

                if "errors" in payload:
                    raise GraphQLException(
                        "\n".join([e["message"] for e in payload["errors"]])
                    )

                if "data" in payload:
                    yield GraphQLResult(data=payload["data"])
                    subscribe_queue.task_done()

            if answer["type"] == WEBSOCKET_DEAD:
                raise SubscriptionDisconnect(
                    f"Subcription {id} failed propagating Error {operation}"
                )

            if answer["type"] == GQL_COMPLETE:
                logger.info(f"Subcription done {operation}")
                return

    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True
