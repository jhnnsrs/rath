from asyncio.tasks import create_task
from typing import Dict
from rath.links.errors import TransportError
from graphql import OperationType
import websockets
import json
import asyncio
from websockets.exceptions import (
    ConnectionClosed,
    ConnectionClosedError,
    ConnectionClosedOK,
)
import logging
import uuid

from rath.operation import GraphQLResult, Operation
from rath.links.base import AsyncTerminatingLink, TerminatingLink, Transport

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


class CorrectableConnectionFail(TransportError):
    pass


class DefiniteConnectionFail(TransportError):
    pass


class InvalidPayload(TransportError):
    pass


class WebSocketLink(AsyncTerminatingLink):
    def __init__(
        self, url="", allow_reconnect=True, time_between_retries=1, retries=3
    ) -> None:
        self.connection_initialized = False
        self.ongoing_subscriptions: Dict[str, asyncio.Queue] = {}
        self.url = url
        self.retries = retries
        self.allow_reconnect = allow_reconnect
        self.time_between_retries = time_between_retries
        pass

    async def aforward(self, message):
        await self.send_queue.put(message)

    async def aconnect(self):
        self.send_queue = asyncio.Queue()
        self.connection_task = create_task(self.websocket_loop())

    async def adisconnect(self):
        self.connection_task.cancel()

        try:
            await self.connection_task
        except asyncio.CancelledError:
            logger.info(f"Websocket Transport {self} succesfully disconnected")

    async def websocket_loop(self, retry=0):
        send_task = None
        receive_task = None
        self.connection_initialized = False
        try:
            try:
                async with websockets.connect(
                    self.url,
                    subprotocols=[GQL_WS_SUBPROTOCOL],
                ) as client:

                    send_task = create_task(self.sending(client))
                    receive_task = create_task(self.receiving(client))

                    self.connection_alive = True
                    self.connection_dead = False
                    done, pending = await asyncio.wait(
                        [send_task, receive_task],
                        return_when=asyncio.FIRST_EXCEPTION,
                    )
                    self.connection_alive = True

                    for task in pending:
                        task.cancel()

                    for task in done:
                        raise task.exception()

            except ConnectionClosedError as e:
                logger.exception(e)
                raise CorrectableConnectionFail from e

            except Exception as e:
                print(e)
                raise CorrectableConnectionFail from e

        except CorrectableConnectionFail as e:
            logger.info(f"Trying to Recover from Exception {e}")
            if retry > self.retries or not self.allow_reconnect:
                raise DefiniteConnectionFail("Exceeded Number of Retries")

            await asyncio.sleep(self.time_between_retries)
            logger.info(f"Retrying to connect")
            await self.websocket_loop(retry=retry + 1)

        except DefiniteConnectionFail as e:
            self.connection_dead = False
            raise e

        except asyncio.CancelledError as e:
            logger.info("Got Canceleld")
            if send_task and receive_task:
                send_task.cancel()
                receive_task.cancel()

            cancellation = await asyncio.gather(
                send_task, receive_task, return_exceptions=True
            )
            raise e

    async def sending(self, client, headers=None):
        payload = {"type": GQL_CONNECTION_INIT, "payload": {"headers": headers}}
        await client.send(json.dumps(payload))

        try:
            while True:
                message = await self.send_queue.get()
                logger.debug("GraphQL Websocket: >>>>>> " + message)
                await client.send(message)
                self.send_queue.task_done()
        except asyncio.CancelledError as e:
            logger.debug("Sending Task sucessfully Cancelled")

    async def receiving(self, client):
        try:
            async for message in client:
                logger.debug("Postman Websocket: <<<<<<< " + message)
                await self.broadcast(message)
        except asyncio.CancelledError as e:
            logger.debug("Receiving Task sucessfully Cancelled")

    async def broadcast(self, res):
        try:
            message = json.loads(res)
        except json.JSONDecodeError as err:
            logger.warning(
                "Ignoring. Server sent invalid JSON data: %s \n %s", res, err
            )

        type = message["type"]

        if type == GQL_CONNECTION_KEEP_ALIVE:
            return

        if type in [GQL_DATA, GQL_COMPLETE]:

            if "id" not in message:
                raise InvalidPayload(f"Protocol Violation. Expected 'id' in {message}")

            id = message["id"]
            assert (
                id in self.ongoing_subscriptions
            ), "Received Result for subscription that is no longer or was never active"
            await self.ongoing_subscriptions[id].put(message)

        print(message)

    async def asubscribe(self, operation: Operation):

        assert (
            operation.node.operation == OperationType.SUBSCRIPTION
        ), "Operation is not a subscription"
        assert (
            operation.context.files is None
        ), "We cannot send files through websockets"

        id = str(uuid.uuid4())
        subscribe_queue = asyncio.Queue()
        self.ongoing_subscriptions[id] = subscribe_queue

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

                if "data" in payload:
                    yield GraphQLResult(data=payload["data"])

            if answer["type"] == GQL_COMPLETE:
                print("Subcription done")
                return

    async def aquery(self, operation: Operation):

        assert (
            operation.node.operation != OperationType.SUBSCRIPTION
        ), "Operation is a subscription. Only queries are allowed on 'aquery'"
        assert (
            operation.context.files is None
        ), "We cannot send files through websockets"

        id = str(uuid.uuid4())
        subscribe_queue = asyncio.Queue()
        self.ongoing_subscriptions[id] = subscribe_queue

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

                if "data" in payload:
                    subscribe_queue.task_done()
                    del self.ongoing_subscriptions[id]
                    return GraphQLResult(data=payload["data"])

            if answer["type"] == GQL_COMPLETE:
                raise InvalidPayload(
                    "Subcription done before yielding data. This shouldnt happen for queries"
                )
