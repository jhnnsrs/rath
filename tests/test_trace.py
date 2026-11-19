"""A request made inside a trace carries it on; outside of one nothing is added."""

from opentelemetry import context, propagate

from rath.trace import traced

TRACEPARENT = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"


def test_outside_of_a_trace_the_headers_are_unchanged() -> None:
    headers = {"Authorization": "Bearer x"}
    assert traced(headers) == headers


def test_inside_a_trace_the_request_carries_it() -> None:
    headers = {"Authorization": "Bearer x"}
    entered = context.attach(propagate.extract({"traceparent": TRACEPARENT}))
    try:
        assert traced(headers) == {"Authorization": "Bearer x", "traceparent": TRACEPARENT}
    finally:
        context.detach(entered)
    assert headers == {"Authorization": "Bearer x"}, "the operation's own headers are left alone"
