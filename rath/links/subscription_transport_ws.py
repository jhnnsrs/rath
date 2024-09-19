from ssl import SSLContext
from typing import AsyncIterator, Dict, Optional, Any
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

WEBSOCKET_DEAD = "websocket_dead"
WEBSOCKET_CANCELLED = "websocket_cancelled"


class CorrectableConnectionFail(TerminatingLinkError):
    """Raied when the connection fails, but can be recovered from"""

    pass


class DefiniteConnectionFail(TerminatingLinkError):
    """Raised when the connection fails, and cannot be recovered from"""

    pass


class InvalidPayload(TerminatingLinkError):
    """Raised when the payload is invalid"""

    pass


async def none_token_loader() -> None:
    """A token loader that always excepts"""
    raise Exception("Token loader was not set")


class SubscriptionTransportWsLink(AsyncTerminatingLink):
    """WebSocketLink is a terminating link that sends operations over websockets using
      websockets via the subscription-transport-ws protocol. This is a
      deprecated protocol, and should not be used for new projects.

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
    """ The SSL Context to use for the connection """
    payload_token_to_querystring: bool = True
    """Should the payload token be sent as a querystring instead (as connection params
      is not supported by all servers)"""

    _connection_lock: Optional[asyncio.Lock] = None
    _connected: bool = False
    _alive: bool = False
    _send_queue: Optional[asyncio.Queue] = None
    _connection_task: Optional[asyncio.Task] = None
    _ongoing_subscriptions: Optional[Dict[str, asyncio.Queue]] = None

    async def aforward(self, message: str) -> None:
        """Forwards a message to the websocket

        Parameters
        ----------
        message : str
            The message to forward

        Raises
        ------
        LinkNotConnectedError
            Raised if the link is not connected
        """
        if not self._send_queue:
            raise LinkNotConnectedError("Link is not connected")
        await self._send_queue.put(message)

    async def __aenter__(self) -> None:
        """Enters the context manager of the link"""
        self._ongoing_subscriptions = {}
        self._send_queue = asyncio.Queue()
        self._connection_lock = asyncio.Lock()

    async def aconnect(self, initiating_operation: Operation) -> None:
        """Connects the websocket

        This method is called automatically when the link is entered.
        It should not be called manually. It needs to received
        an initiating operation, which is used to build the connection
        payload. It succeds when the connection is established, and fails
        if the connection cannot be established.

        Parameters
        ----------
        initiating_operation : Operation
            The initiating operation

        """
        logger.info("Connecting Websockets")
        connection_future = asyncio.get_running_loop().create_future()
        self._connection_task = asyncio.create_task(
            self.websocket_loop(initiating_operation, connection_future)
        )
        await connection_future

    async def adisconnect(self) -> None:
        """Disconnects the websocket"""
        if self._connection_task:
            self._connection_task.cancel()

            try:
                await self._connection_task
            except asyncio.CancelledError:
                logger.info(f"Websocket Transport {self} succesfully disconnected")

    async def __aexit__(self, *args, **kwargs) -> None:
        """Exits the context manager of the link"""
        await self.adisconnect()

    async def build_url(self, initiating_operation: Operation) -> str:
        """Builds the url for the websocket

        It uses the initiating operation to build the url. By default
        it will use the payload token as a querystring, but this can be
        disabled by setting payload_token_to_querystring to False.

        Parameters
        ----------
        initiating_operation : Operation
            The initiating operation

        Returns
        -------
        str
            The url for the websocket
        """
        if self.payload_token_to_querystring:
            token = initiating_operation.context.initial_payload.get("token", None)
            return (
                f"{self.ws_endpoint_url}?token={token}"
                if token
                else self.ws_endpoint_url
            )
        else:
            return self.ws_endpoint_url

    async def websocket_loop(
        self,
        initiating_operation: Operation,
        connection_future: asyncio.Future,
        retry: int = 0,
    ) -> None:
        """The main websocket loop

        This method is the main websocket loop. It will try to connect to the
        websocket, and will retry if it fails. It will also try to reconnect
        if the connection is lost.
        You should not call this method manually.
        """
        send_task = None
        receive_task = None
        try:
            try:
                url = await self.build_url(initiating_operation)
                async with websockets.connect(  # type: ignore
                    url,
                    subprotocols=[GQL_WS_SUBPROTOCOL],
                    ssl=self.ssl_context if url.startswith("wss") else None,
                ) as client:
                    logger.info("Websocket successfully connected")

                    send_task = asyncio.create_task(
                        self.sending(client, initiating_operation)
                    )
                    receive_task = asyncio.create_task(
                        self.receiving(client, initiating_operation, connection_future)
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
            logger.info("Retrying to connect")
            await self.broadcast(
                {"type": WEBSOCKET_DEAD, "error": e}, connection_future
            )
            await self.websocket_loop(
                initiating_operation, connection_future, retry=retry + 1
            )

        except DefiniteConnectionFail as e:
            logger.error("Websocket excepted closed definetely", exc_info=True)
            self.connection_dead = True
            if connection_future and not connection_future.done():
                connection_future.set_exception(e)
            raise e

        except asyncio.CancelledError as e:
            logger.info("Websocket got cancelled. Trying to shutdown graceully")
            if send_task and receive_task:
                send_task.cancel()
                receive_task.cancel()

                await asyncio.gather(send_task, receive_task, return_exceptions=True)
            raise e

        except Exception as e:
            logger.error("Websocket excepted", exc_info=True)
            self.connection_dead = True
            if connection_future and not connection_future.done():
                connection_future.set_exception(e)
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
            "payload": {"headers": initiating_operation.context.headers},
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
        self,
        client: Any,
        initiating_operation: Operation,
        connection_future: asyncio.Future,
    ) -> None:
        """The receiving task

        This method is the receiving task. It will receive messages from the websocket
        and broadcast them to the subscriptions. It should not be called manually.
        but is called automatically by the websocket loop.

        Parameters
        ----------
        client : websocket.Client
            The websockets client
        initiating_operation : Operation
            The initiating operation
        connection_future : asyncio.Future
            The future to set when the connection is established



        """
        try:
            async for message in client:
                logger.debug("GraphQL Websocket: <<<<<<< " + message)
                try:
                    message = json.loads(message)
                    await self.broadcast(message, connection_future)
                except json.JSONDecodeError as err:
                    logger.warning(
                        "Ignoring. Server sent invalid JSON data: %s \n %s",
                        message,
                        err,
                    )
        except Exception as e:
            logger.warning("Websocket excepted. Trying to recover", exc_info=True)
            raise e

    async def broadcast(self, message: dict, connection_future: asyncio.Future) -> None:
        """Broadcasts a message to the subscriptions, or handles it internally
        e.g if it is a connection ack message.

        Parameters
        ----------
        message : dict
            The message to broadcast ( already json parsed)
        connection_future : asyncio.Future
            The future to set when the connection is established
        """
        type = message["type"]

        if type == GQL_CONNECTION_ACK:
            if connection_future and not connection_future.done():
                connection_future.set_result(True)
            return

        if type == GQL_CONNECTION_KEEP_ALIVE:
            if connection_future and not connection_future.done():
                connection_future.set_result(True)
            return

        if type == WEBSOCKET_DEAD:
            # notify all subscriptipns that the websocket is dead
            if not self._ongoing_subscriptions:
                self._ongoing_subscriptions = {}

            for subscription in self._ongoing_subscriptions.values():
                await subscription.put(message)
            return

        if type in [GQL_DATA, GQL_COMPLETE]:
            if "id" not in message:
                raise InvalidPayload(f"Protocol Violation. Expected 'id' in {message}")

            id = message["id"]
            if not self._ongoing_subscriptions:
                self._ongoing_subscriptions = {}

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
            raise Exception(
                "WebsocketLink not entered yet. Please us this in an async context manager"
            )

        async with self._connection_lock:
            if self._connection_task is None or self._connection_task.done():
                await self.aconnect(operation)

        assert (
            operation.node.operation == OperationType.SUBSCRIPTION
        ), "Operation is not a subscription"
        assert not operation.context.files, "We cannot send files through websockets"

        id = operation.id
        subscribe_queue = asyncio.Queue()  # type: asyncio.Queue

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
