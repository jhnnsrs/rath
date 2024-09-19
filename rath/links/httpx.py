from http import HTTPStatus
import json
from typing import Any, Dict, List, Type, AsyncIterator
import httpx
from graphql import OperationType
from pydantic import Field
from rath.operation import GraphQLException, GraphQLResult, Operation
from rath.links.base import AsyncTerminatingLink
from rath.links.errors import AuthenticationError
import logging
from rath.links.types import Payload
from datetime import datetime

logger = logging.getLogger(__name__)


class DateTimeEncoder(json.JSONEncoder):
    """DateTimeEncoder is a JSONEncoder that extends the default python json decoder to serialize"""

    def default(self, o):  # noqa
        """Override the default method to serialize datetime objects to ISO 8601 strings"""
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


class HttpxLink(AsyncTerminatingLink):
    """HttpxLink is a terminating link that sends operations over HTTP using httpx"""

    endpoint_url: str
    """endpoint_url is the URL to send operations to."""

    auth_errors: List[HTTPStatus] = Field(
        default_factory=lambda: (HTTPStatus.FORBIDDEN,)
    )
    """auth_errors is a list of HTTPStatus codes that indicate an authentication error."""
    json_encoder: Type[json.JSONEncoder] = Field(default=DateTimeEncoder, exclude=True)

    async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
        """Executes an operation against the link

        This link will create a new httpx session for each request. While
        we could also reuse the session, we currently don't do this. If
        you feel like this should be changed, please open an issue.

        Parameters
        ----------
        operation : Operation
            The operation to execute

        Yields
        ------
        GraphQLResult
            The result of the operation
        """

        payload: Payload = {"query": operation.document}

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

        async with httpx.AsyncClient() as client:
            response = await client.post(
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
