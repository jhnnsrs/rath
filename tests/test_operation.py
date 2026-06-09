"""Tests for operation.py – opify(), Context, Operation, and exception classes."""
import pytest
from graphql import DocumentNode

from rath.operation import (
    Context,
    Extensions,
    GraphQLException,
    GraphQLResult,
    Operation,
    SubscriptionDisconnect,
    opify,
)
from rath.errors import (
    NotComposedError,
    NotConnectedError,
    NotEnteredError,
    RathException,
)
from rath.links.errors import (
    AuthenticationError,
    ContinuationLinkError,
    LinkError,
    LinkNotConnectedError,
    MalformedResponseError,
    TerminatingLinkError,
    TokenLoaderNotSetError,
    TokenRefresherNotSetError,
)


# ---------------------------------------------------------------------------
# opify()
# ---------------------------------------------------------------------------


def test_opify_returns_operation():
    op = opify("query { hello }")
    assert isinstance(op, Operation)


def test_opify_parses_document_string():
    op = opify("query { hello }")
    assert isinstance(op.document_node, DocumentNode)


def test_opify_stores_printed_document():
    op = opify("query { hello }")
    assert "hello" in op.document


def test_opify_with_variables():
    op = opify("query($id: ID!) { user(id: $id) { name } }", variables={"id": "1"})
    assert op.variables == {"id": "1"}


def test_opify_without_variables_defaults_to_empty_dict():
    op = opify("query { hello }")
    assert op.variables == {}


def test_opify_with_headers():
    op = opify("query { hello }", headers={"Authorization": "Bearer tok"})
    assert op.context.headers["Authorization"] == "Bearer tok"


def test_opify_without_headers_defaults_to_empty_dict():
    op = opify("query { hello }")
    assert op.context.headers == {}


def test_opify_with_operation_name():
    op = opify(
        "query GetHello { hello } query Other { world }",
        operation_name="GetHello",
    )
    assert op.operation_name == "GetHello"


def test_opify_generates_unique_ids():
    op1 = opify("query { hello }")
    op2 = opify("query { hello }")
    assert op1.id != op2.id


def test_opify_accepts_document_node():
    from graphql import parse

    document = parse("query { hello }")
    op = opify(document)
    assert isinstance(op.document_node, DocumentNode)


def test_opify_raises_on_missing_operation():
    """opify raises when the named operation is not in the document."""
    with pytest.raises(AssertionError):
        opify("query { hello }", operation_name="NonExistent")


# ---------------------------------------------------------------------------
# Context defaults
# ---------------------------------------------------------------------------


def test_context_has_empty_defaults():
    ctx = Context()
    assert ctx.headers == {}
    assert ctx.files == {}
    assert ctx.initial_payload == {}
    assert ctx.kwargs == {}
    assert ctx.extensions == {}
    assert ctx.omit_document is False


def test_context_extensions_can_be_mutated():
    ctx = Context()
    ctx.extensions["key"] = "value"
    assert ctx.extensions["key"] == "value"


def test_context_omit_document_can_be_set():
    ctx = Context()
    ctx.omit_document = True
    assert ctx.omit_document is True


def test_context_headers_mutated_via_dict():
    ctx = Context()
    ctx.headers["Authorization"] = "Bearer x"
    assert ctx.headers["Authorization"] == "Bearer x"


# ---------------------------------------------------------------------------
# Extensions defaults
# ---------------------------------------------------------------------------


def test_extensions_defaults_are_none():
    ext = Extensions()
    assert ext.pollInterval is None
    assert ext.maxPolls is None


# ---------------------------------------------------------------------------
# GraphQLResult
# ---------------------------------------------------------------------------


def test_graphql_result_stores_data():
    r = GraphQLResult(data={"key": "value"})
    assert r.data == {"key": "value"}


def test_graphql_result_equality():
    r1 = GraphQLResult(data={"a": 1})
    r2 = GraphQLResult(data={"a": 1})
    assert r1 == r2


# ---------------------------------------------------------------------------
# GraphQLException
# ---------------------------------------------------------------------------


def test_graphql_exception_message():
    exc = GraphQLException("something went wrong")
    assert exc.message == "something went wrong"
    assert str(exc) == str(exc)  # __str__ does not crash


def test_graphql_exception_str_includes_message():
    exc = GraphQLException("bad query")
    assert "bad query" in str(exc)


def test_graphql_exception_str_includes_endpoint():
    exc = GraphQLException("err", endpoint_url="http://example.com/graphql")
    assert "http://example.com/graphql" in str(exc)


def test_graphql_exception_str_includes_operation_name():
    op = opify("query MyOp { hello }", operation_name="MyOp")
    exc = GraphQLException("err", operation=op)
    assert "MyOp" in str(exc)


def test_graphql_exception_str_falls_back_to_document_name():
    """Even without an explicit operation_name, the document's name is surfaced."""
    op = opify("query MyOp { hello }")  # note: no operation_name passed
    assert op.operation_name is None
    exc = GraphQLException("err", operation=op)
    assert "MyOp" in str(exc)


def test_operation_display_name_prefers_explicit_name():
    op = opify("query MyOp { hello }")
    op.operation_name = "Override"  # explicit name wins over the document name
    assert op.display_name == "Override"


def test_operation_display_name_falls_back_to_node_name():
    op = opify("query MyOp { hello }")
    assert op.display_name == "MyOp"


def test_operation_display_name_handles_anonymous_operations():
    op = opify("{ hello }")
    assert op.display_name == "Unnamed Operation"


def test_graphql_exception_with_errors_dict():
    exc = GraphQLException("err", errors={"code": "NOT_FOUND"})
    assert exc.errors == {"code": "NOT_FOUND"}


def test_graphql_exception_errors_default_is_empty_dict():
    exc = GraphQLException("err")
    assert exc.errors == {}


def test_graphql_exception_is_exception():
    exc = GraphQLException("fail")
    with pytest.raises(GraphQLException):
        raise exc


# ---------------------------------------------------------------------------
# SubscriptionDisconnect
# ---------------------------------------------------------------------------


def test_subscription_disconnect_is_graphql_exception():
    exc = SubscriptionDisconnect("disconnected")
    assert isinstance(exc, GraphQLException)


def test_subscription_disconnect_can_be_raised():
    with pytest.raises(SubscriptionDisconnect):
        raise SubscriptionDisconnect("gone")


# ---------------------------------------------------------------------------
# rath.errors hierarchy
# ---------------------------------------------------------------------------


def test_not_composed_error_is_rath_exception():
    assert issubclass(NotComposedError, RathException)


def test_not_connected_error_is_rath_exception():
    assert issubclass(NotConnectedError, RathException)


def test_not_entered_error_is_rath_exception():
    assert issubclass(NotEnteredError, RathException)


# ---------------------------------------------------------------------------
# links.errors hierarchy
# ---------------------------------------------------------------------------


def test_authentication_error_is_terminating_link_error():
    assert issubclass(AuthenticationError, TerminatingLinkError)


def test_terminating_link_error_is_link_error():
    assert issubclass(TerminatingLinkError, LinkError)


def test_continuation_link_error_is_link_error():
    assert issubclass(ContinuationLinkError, LinkError)


def test_link_not_connected_error_message_has_hint():
    exc = LinkNotConnectedError("base msg")
    assert "context manager" in str(exc).lower()


# ---------------------------------------------------------------------------
# new informative error classes
# ---------------------------------------------------------------------------


def test_token_loader_not_set_error_is_continuation_link_error():
    assert issubclass(TokenLoaderNotSetError, ContinuationLinkError)


def test_token_refresher_not_set_error_is_continuation_link_error():
    assert issubclass(TokenRefresherNotSetError, ContinuationLinkError)


def test_malformed_response_error_is_terminating_link_error():
    assert issubclass(MalformedResponseError, TerminatingLinkError)


def test_new_errors_are_rath_exceptions():
    for cls in (
        TokenLoaderNotSetError,
        TokenRefresherNotSetError,
        MalformedResponseError,
    ):
        assert issubclass(cls, RathException)


def test_token_loader_not_set_error_message_is_actionable():
    exc = TokenLoaderNotSetError(
        "No Token loader specified. Subclass AuthTokenLink and override aload_token."
    )
    assert "aload_token" in str(exc)


def test_malformed_response_error_can_carry_context():
    exc = MalformedResponseError(
        "Response from http://x/graphql for operation 'Foo' contains neither 'data' nor 'errors': {}"
    )
    assert "http://x/graphql" in str(exc)
    assert "Foo" in str(exc)
