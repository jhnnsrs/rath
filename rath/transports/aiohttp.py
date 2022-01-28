import asyncio
from http import HTTPStatus
import json
from multiprocessing import AuthenticationError
from typing import Any, Dict

import aiohttp
from graphql import OperationType
from rath.operation import GraphQLResult, Operation
from rath.transports.base import Transport


class AIOHttpTransport(Transport):

    auth_errors = [HTTPStatus.FORBIDDEN]

    def __init__(self, url: str) -> None:
        super().__init__()
        self.url = url

    async def aquery(self, operation: Operation) -> GraphQLResult:
        payload = {"query": operation.document}

        if len(operation.context.files.items()) > 0:
            payload["variables"] = operation.variables

            files = operation.context.files
            data = aiohttp.FormData()

            file_map = {str(i): [path] for i, path in enumerate(files)}

            # Enumerate the file streams
            # Will generate something like {'0': <_io.BufferedReader ...>}
            file_streams = {str(i): files[path] for i, path in enumerate(files)}
            operations_str = json.dumps(payload)

            data.add_field(
                "operations", operations_str, content_type="application/json"
            )
            file_map_str = json.dumps(file_map)
            data.add_field("map", file_map_str, content_type="application/json")

            for k, v in file_streams.items():
                data.add_field(
                    k,
                    v,
                    filename=getattr(v, "name", k),
                )

            post_kwargs: Dict[str, Any] = {"data": data}

        else:
            payload["variables"] = operation.variables
            post_kwargs = {"json": payload}

        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, **post_kwargs) as response:

                if response.status == HTTPStatus.OK:
                    result = await response.json()

                if response.status in self.auth_errors:
                    raise AuthenticationError("Token Expired Error")

                json_response = await response.json()

                if "data" not in json_response:
                    raise Exception("Response does not contain data")

                return GraphQLResult(data=json_response["data"])

    async def asubscribe(self, operation: Operation) -> GraphQLResult:
        if operation.node.operation == OperationType.SUBSCRIPTION:
            raise NotImplementedError(
                "Aiohttp Transport does not support subscriptions"
            )

        if operation.node.operation == OperationType.QUERY:
            if operation.extensions.pollInterval:
                while True:
                    yield await self.aquery(operation)
                    await asyncio.sleep(operation.extensions.pollInterval)
            else:
                raise NotImplementedError(
                    "If you didn't specify a pollInterval you cannot use subscribe to this query"
                )
