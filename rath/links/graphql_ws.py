from ssl import SSLContext
from typing import AsyncIterator, Awaitable, Callable, Dict, Optional, Any
from graphql import OperationType
from pydantic import Field
import websockets
import json
import asyncio
import logging
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

GQL_PING = "ping"
GQL_PONG = "pong"

WEBSOCKET_DEAD = "websocket_dead"
WEBSOCKET_CANCELLED = "websocket_cancelled"


class CorrectableConnectionFail(TerminatingLinkError):
    """A CorrectableConnectionFail is raised when a connection fails, but can be recovered from"""

    pass


class DefiniteConnectionFail(TerminatingLinkError):
    """A DefiniteConnectionFail is raised when a connection fails, and cannot be recovered from"""

    pass


class InvalidPayload(TerminatingLinkError):
    """A InvalidPayload is raised when a invalid payload is received"""

    pass


InitialConnectPayload = Dict[str, Any]
PongPayload = Dict[str, Any]


class GraphQLWSLink(AsyncTerminatingLink):
    """GraphQLWSLink is a terminating link that sends operations over websockets using
      websockets via the graphql-ws protocol. This is a
      new standard protocol, and should not be used for new projects.

    This is a terminating link, so it should be the last link in the chain.
    This is a stateful link, keeing a connection open and sending messages over it.

    """

    ws_endpoint_url: str
    """ The endpoint url to connect to """
    allow_reconnect: bool = True
    """ Should the websocket try to reconnect if it fails """
    time_between_retries: float = 4
    """ The sleep time between retries """
    max_retries: int = 3
    """ The maximum amount of retries before giving up """
    ssl_context: SSLContext = Field(
        default_factory=lambda: ssl.create_default_context(cafile=certifi.where())
    )

    on_connect: Optional[Callable[[InitialConnectPayload], Awaitable[None]]] = Field(
        exclude=True, default=None
    )
    """ A function that is called before the connection is established. If an exception is raised, the connection is not established. Return is ignored."""

    on_pong: Optional[Callable[[PongPayload], Awaitable[None]]] = Field(
        exclude=True, default=None
    )
    """ A function that is called before a pong is received. If an exception is raised, the connection is not established. Return is ignored."""
    heartbeat_interval_ms: Optional[int] = None
    """ The heartbeat interval in milliseconds (None means no heartbeats are 
    being send) """

    _connection_lock: Optional[asyncio.Lock] = None
    _connected: bool = False
    _alive: bool = False
    _send_queue: Optional[asyncio.Queue] = None
    _connection_task: Optional[asyncio.Task] = None
    _ongoing_subscriptions: Optional[Dict[str, asyncio.Queue]] = None

    async def aforward(self, message: str) -> None:
        """Forward a message to the server

        Puts the message in the send queue. If the queue is full, this will block until
        the queue is not full anymore.

        Parameters
        ----------
        message : str
            The message to send
        """
        if not self._send_queue:
            raise LinkNotConnectedError("Link is not connected")

        await self._send_queue.put(message)

    async def __aenter__(self) -> None:
        """Enter the link, and initialize the connection"""

        self._ongoing_subscriptions = {}
        self._connection_lock = asyncio.Lock()
        self._send_queue = asyncio.Queue()

    async def aconnect(self, operation: Operation) -> None:
        """Connect to the server

        Parameters
        ----------
        operation : Operation
            The operation that is used for the first time to connect to the server
            can be used to send an initial payload
        """

        logger.info("Connecting Websockets")
        initial_connection_future = asyncio.get_running_loop().create_future()
        self._connection_task = asyncio.create_task(
            self.websocket_loop(operation, initial_connection_future)
        )
        await initial_connection_future

    async def adisconnect(self) -> None:
        """Disconnect from the server"""
        if self._connection_task:
            self._connection_task.cancel()

            try:
                await self._connection_task
            except asyncio.CancelledError:
                logger.info("Websocket Transport succesfully disconnected")

    async def __aexit__(self, *args, **kwargs) -> None:
        """Exit the link, and disconnect from the server"""
        await self.adisconnect()

    async def abuild_url(self, initiating_operation: Operation) -> str:
        """Builds the url to connect to

        This can be overwritten to add additional parameters to the url
        like authentication tokens

        Parameters
        ----------
        initiating_operation : Operation
            The operation that is used for the first time to connect to the server

        Returns
        -------
        str
            The url to connect to
        """
        return self.ws_endpoint_url

    async def websocket_loop(
        self,
        initiating_operation: Operation,
        initial_connection_future: asyncio.Future,
        retry: int = 0,
    ) -> None:
        """The main websocket loop

        This is the main loop that handles the websocket connection.
        It handles all the sending and receiving of messages.
        """
        send_task = None
        receive_task = None
        try:
            try:
                url = await self.abuild_url(initiating_operation)
                async with websockets.connect(  # type: ignore
                    url,
                    subprotocols=[GQL_WS_SUBPROTOCOL],
                    ssl=self.ssl_context if url.startswith("wss") else None,
                ) as client:
                    logger.info("Websocket successfully connected")

                    send_task = asyncio.create_task(
                        self.sending(
                            client,
                            initiating_operation,
                        )
                    )
                    receive_task = asyncio.create_task(
                        self.receiving(client, initial_connection_future)
                    )

                    self._alive = True
                    done, pending = await asyncio.wait(
                        [send_task, receive_task],
                        return_when=asyncio.FIRST_EXCEPTION,
                    )
                    self._alive = False

                    for task in pending:
                        task.cancel()

                    for task in done:
                        exception = task.exception()
                        if exception:
                            raise exception
                        else:
                            raise CorrectableConnectionFail(
                                f"Websocket connection closed without exception: This is unexpected behaviours. Results ist {task.result()}"
                            )

            except Exception as e:
                logger.warning(
                    f"Websocket excepted. Trying to recover for the {retry+1}/{self.max_retries} time",
                    exc_info=True,
                )
                raise CorrectableConnectionFail from e

        except CorrectableConnectionFail as e:
            logger.info(
                f"Trying to Recover from Exception {e} Reconnect is {self.allow_reconnect} Retry: {retry}"
            )
            if retry > self.max_retries or not self.allow_reconnect:
                logger.error("Max retries reached. Aborting")
                raise DefiniteConnectionFail("Exceeded Number of Retries")

            await asyncio.sleep(self.time_between_retries)
            logger.info("Retrying to connect")
            await self.broadcast(
                {"type": WEBSOCKET_DEAD, "error": e}, initial_connection_future
            )
            await self.websocket_loop(
                initiating_operation, initial_connection_future, retry=retry + 1
            )

        except DefiniteConnectionFail as e:
            logger.error("Websocket excepted closed definetely", exc_info=True)
            self.connection_dead = True
            raise e

        except asyncio.CancelledError as e:
            logger.info("Websocket got cancelled. Trying to shutdown graceully")
            if send_task and receive_task:
                send_task.cancel()
                receive_task.cancel()

                await asyncio.gather(
                    send_task, receive_task, return_exceptions=True
                )  # wait for the tasks to finish
            raise e

        except Exception as e:
            logger.error("Websocket excepted", exc_info=True)
            self.connection_dead = True
            raise e

    async def sending(self, client: Any, initiating_operation: Operation) -> None:
        """The sending task

        This method is the sending task. It will send messages to the websocket
        as they are put into the send queue.  It should not be called manually.
        but is called automatically by the websocket loop.


        Parameters
        ----------
        client : websocket.Client
            The websockets client
        initiating_operation : Operation
            The initiating operation

        """

        payload = {
            "type": GQL_CONNECTION_INIT,
            "payload": initiating_operation.context.initial_payload,
        }
        await client.send(json.dumps(payload))

        try:
            while True:
                if not self._send_queue:
                    raise LinkNotConnectedError("Link is not connected")

                message = await self._send_queue.get()
                logger.debug("GraphQL Websocket: >>>>>> " + message)
                await client.send(message)
                self._send_queue.task_done()
        except asyncio.CancelledError as e:
            logger.debug("Sending Task sucessfully Cancelled")  #
            raise e

    async def receiving(
        self, client: Any, initial_connection_future: asyncio.Future
    ) -> None:
        """The receiving task

        This method is the receiving task. It will receive messages from the websocket
        and broadcast them to the subscriptions. It should not be called manually.
        but is called automatically by the websocket loop.

        Parameters
        ----------
        client : websocket.Client
            The websockets client
        connection_future : asyncio.Future
            The future to set when the connection is established

        """
        try:
            async for message in client:
                logger.debug("GraphQL Websocket: <<<<<<< " + message)
                try:
                    message = json.loads(message)
                    await self.broadcast(message, initial_connection_future)
                except json.JSONDecodeError as err:
                    logger.warning(
                        "Ignoring. Server sent invalid JSON data: %s \n %s",
                        message,
                        err,
                    )
        except Exception as e:
            logger.warning("Websocket excepted. Trying to recover", exc_info=True)
            raise e

    async def broadcast(
        self, message: dict, initial_connection_future: asyncio.Future
    ) -> None:
        """Broadcasts a message to all subscriptions"""
        type = message["type"]

        if type == GQL_CONNECTION_ACK:
            if self.on_connect:
                await self.on_connect(message.get("payload", {}))
            initial_connection_future.set_result(True)
            return

        if type == GQL_PING:
            if self.on_pong:
                await self.on_pong(message.get("payload", {}))

            payload = message.get("payload", {})
            await self.aforward(json.dumps({"type": GQL_PONG, "payload": payload}))

        if type == GQL_CONNECTION_KEEP_ALIVE:
            return

        if type == WEBSOCKET_DEAD:
            # notify all subscriptipns that the websocket is dead
            if not self._ongoing_subscriptions:
                self._ongoing_subscriptions = {}

            for subscription in self._ongoing_subscriptions.values():
                await subscription.put(message)
            return

        if type in [GQL_DATA, GQL_COMPLETE, GQL_ERROR]:
            if not self._ongoing_subscriptions:
                self._ongoing_subscriptions = {}

            if "id" not in message:
                raise InvalidPayload(f"Protocol Violation. Expected 'id' in {message}")

            id = message["id"]
            assert (
                id in self._ongoing_subscriptions
            ), "Received Result for subscription that is no longer or was never active"
            await self._ongoing_subscriptions[id].put(message)

    async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
        """Executes an operation against the link

        This link will send the operation to the websocket, and then
        wait for the result.

        Parameters
        ----------
        operation : Operation
            The operation to execute

        Yields
        ------
        GraphQLResult
            The result of the operation
        """
        if not self._connection_lock:
            raise LinkNotConnectedError("Link is not connected")

        async with self._connection_lock:
            if self._connection_task is None or self._connection_task.done():
                # we need to start a new connection
                await self.aconnect(operation)

        assert (
            operation.node.operation == OperationType.SUBSCRIPTION
        ), "Operation is not a subscription"
        assert not operation.context.files, "We cannot send files through websockets"

        id = operation.id
        subscribe_queue = asyncio.Queue()  # type: ignore
        if not self._ongoing_subscriptions:
            self._ongoing_subscriptions = {}

        self._ongoing_subscriptions[id] = subscribe_queue

        send_payload = {
            "headers": operation.context.headers,
            "query": operation.document,
            "variables": operation.variables,
        }

        try:
            frame = {"id": id, "type": GQL_START, "payload": send_payload}
            await self.aforward(json.dumps(frame))
            logger.debug(f"Subcription started {operation}")

            while True:
                answer = await subscribe_queue.get()

                if answer["type"] == GQL_ERROR:
                    payload = answer["payload"]
                    if isinstance(payload, list):
                        error_list = payload
                    else:
                        error_list = [payload]

                    raise GraphQLException(
                        "\n".join([e["message"] for e in error_list])
                    )

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

        except asyncio.CancelledError as e:
            logger.debug(f"Subcription ended {operation}")
            await self.aforward(json.dumps({"id": id, "type": GQL_STOP}))
            raise e
