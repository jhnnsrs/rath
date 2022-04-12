from http import HTTPStatus
import json
from typing import Any, Dict, List

import aiohttp
from aiohttp.typedefs import JSONEncoder
from graphql import OperationType
from rath.json.encoders import dumps
from pydantic import Field
from rath.operation import GraphQLException, GraphQLResult, Operation
from rath.links.base import AsyncTerminatingLink
from rath.links.errors import AuthenticationError
import logging

logger = logging.getLogger(__name__)


class AIOHttpLink(AsyncTerminatingLink):
    url: str
    auth_errors: List[HTTPStatus] = Field(
        default_factory=lambda: (HTTPStatus.FORBIDDEN,)
    )

    _session = None
    _json_encoder: JSONEncoder = dumps

    async def __aenter__(self) -> None:
        self._session = await aiohttp.ClientSession(
            json_serialize=self._json_encoder
        ).__aenter__()

    async def __aexit__(self, *args, **kwargs) -> None:
        await self._session.__aexit__(*args, **kwargs)

    async def aexecute(self, operation: Operation) -> GraphQLResult:
        payload = {"query": operation.document}

        if operation.node.operation == OperationType.SUBSCRIPTION:
            raise NotImplementedError(
                "Aiohttp Transport does not support subscriptions"
            )

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

        async with self._session.post(
            self.url, headers=operation.context.headers, **post_kwargs
        ) as response:

            if response.status == HTTPStatus.OK:
                result = await response.json()

            if response.status in self.auth_errors:
                raise AuthenticationError(
                    f"Token Expired Error {operation.context.headers}"
                )

            json_response = await response.json()

            if "errors" in json_response:
                raise GraphQLException(
                    "\n".join([e["message"] for e in json_response["errors"]])
                )

            if "data" not in json_response:

                raise Exception(f"Response does not contain data {json_response}")

            yield GraphQLResult(data=json_response["data"])

    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True
