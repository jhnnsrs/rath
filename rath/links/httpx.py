from datetime import datetime
from http import HTTPStatus
import json
from ssl import SSLContext
from typing import Any, Dict, List, Type
import httpx
import aiohttp
from graphql import OperationType
from pydantic import Field
from rath.operation import GraphQLException, GraphQLResult, Operation
from rath.links.base import AsyncTerminatingLink
from rath.links.errors import AuthenticationError
import logging
import certifi
import ssl

logger = logging.getLogger(__name__)


class HttpxLink(AsyncTerminatingLink):
    """HttpxLink is a terminating link that sends operations over HTTP using httpx"""

    endpoint_url: str
    """endpoint_url is the URL to send operations to."""

    auth_errors: List[HTTPStatus] = Field(
        default_factory=lambda: (HTTPStatus.FORBIDDEN,)
    )
    """auth_errors is a list of HTTPStatus codes that indicate an authentication error."""

    _client = None

    async def __aenter__(self) -> None:
        self._client = await httpx.AsyncClient().__aenter__()

    async def __aexit__(self, *args, **kwargs) -> None:
        await self._client.__aexit__(*args, **kwargs)

    async def aexecute(self, operation: Operation) -> GraphQLResult:
        payload = {"query": operation.document}

        if operation.node.operation == OperationType.SUBSCRIPTION:
            raise NotImplementedError(
                "Aiohttp Transport does not support subscriptions"
            )

        if len(operation.context.files.items()) > 0:
            payload["variables"] = operation.variables

            files = operation.context.files

            file_map = {str(i): [path] for i, path in enumerate(files)}

            # Enumerate the file streams
            # Will generate something like {'0': <_io.BufferedReader ...>}
            file_streams = {str(i): files[path] for i, path in enumerate(files)}
            operations_str = json.dumps(payload, cls=self.json_encoder)
            file_map_str = json.dumps(file_map)

            post_kwargs: Dict[str, Any] = {
                "data": {
                    "operations": operations_str,
                    "map": file_map_str,
                },
                "files": file_streams,
            }

        else:
            payload["variables"] = operation.variables
            post_kwargs = {"json": payload}

        response = await self._client.post(
            self.endpoint_url, headers=operation.context.headers, **post_kwargs
        )

        if response.status_code in self.auth_errors:
            raise AuthenticationError(
                f"Token Expired Error {operation.context.headers}"
            )

        if response.status_code == HTTPStatus.OK:

            json_response = response.json()

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
