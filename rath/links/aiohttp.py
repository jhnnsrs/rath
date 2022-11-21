from datetime import datetime
from http import HTTPStatus
import json
from ssl import SSLContext
from typing import Any, Dict, List, Type

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


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


class AIOHttpLink(AsyncTerminatingLink):
    """AIOHttpLink is a terminating link that sends operations over HTTP using aiohttp.

    Aiohttp is a Python library for asynchronous HTTP requests. This link uses the
    standard aiohttp library to send operations over HTTP, but provides an ssl context
    that is configured to use the certifi CA bundle by default. You can override this
    behavior by passing your own SSLContext to the constructor.
    """
    endpoint_url: str
    """endpoint_url is the URL to send operations to."""
    ssl_context: SSLContext = Field(
        default_factory=lambda: ssl.create_default_context(cafile=certifi.where())
    )
    """ssl_context is the SSLContext to use for the aiohttp session. By default, this
    is a context that uses the certifi CA bundle."""

    auth_errors: List[HTTPStatus] = Field(
        default_factory=lambda: (HTTPStatus.FORBIDDEN,)
    )
    """auth_errors is a list of HTTPStatus codes that indicate that the request was
    unauthorized. By default, this is just HTTPStatus.FORBIDDEN, but you can
    override this to include other status codes that indicate that the request was
    unauthorized."""

    json_encoder: Type[json.JSONEncoder] = Field(default=DateTimeEncoder, exclude=True)
    """json_encoder is the JSONEncoder to use when serializing the payload. By default,
    this is a DateTimeEncoder that extends the default python json decoder to serializes datetime objects to ISO 8601 strings."""

    _session = None

    async def __aenter__(self) -> None:
        self._session = await aiohttp.ClientSession().__aenter__()

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
            operations_str = json.dumps(payload, cls=self.json_encoder)

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

        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=self.ssl_context),
            json_serialize=lambda x: json.dumps(x, cls=self.json_encoder),
        ) as session:
            async with session.post(
                self.endpoint_url, headers=operation.context.headers, **post_kwargs
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
