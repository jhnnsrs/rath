from graphql import OperationType
from rath.links import compose
from rath.links.sign_local_link import ComposedSignTokenLink, SignLocalLink
from rath.links.testing.assert_link import AssertLink
from rath.links.testing.utils import run_basic_query
from rath.operation import Operation


def test_serialization() -> None:
    SignLocalLink(private_key="private_key.pem")


async def test_sign_local_link() -> None:
    def is_query(op: Operation) -> bool:
        print(op.document_node.kind)
        return op.node.operation == OperationType.QUERY

    def has_token_header(op: Operation) -> bool:
        return op.context.headers.get("Authorization") is not None

    async def load_payload(operation: Operation) -> dict[str, str]:
        return {
            "sub": "1234567890",
        }

    x = compose(
        ComposedSignTokenLink(
            private_key="private_key.pem", payload_retriever=load_payload
        ),
        AssertLink(assertions=[has_token_header, is_query]),
    )
    await run_basic_query(x)
