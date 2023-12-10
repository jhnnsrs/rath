from graphql import OperationType
from rath.links.testing.assert_link import AssertLink
from rath.links.testing.utils import run_basic_query
from rath.links.testing.statefulmock import AsyncStatefulMockLink
from rath.links.sign_local_link import SignLocalLink, ComposedSignTokenLink
import pytest
from rath.links import split, compose
from rath import Rath
from rath.operation import Operation


def test_serialization():
    link = SignLocalLink(private_key="private_key.pem")


async def test_sign_local_link():
    def is_query(op: Operation):
        print(op.document_node.kind)
        return op.node.operation == OperationType.QUERY

    def has_token_header(op: Operation):
        return op.context.headers.get("token") is not None

    async def load_payload(operation: Operation):
        return {
            "sub": "1234567890",
        }

    x = compose(
        ComposedSignTokenLink(
            private_key="private_key.pem", payload_retriever=load_payload
        ),
        AssertLink(assertions=[is_query]),
    )
    await run_basic_query(x)
