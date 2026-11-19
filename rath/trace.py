"""The trace a request is made in (W3C Trace Context, through OpenTelemetry's API).

A request made inside a trace says so (``traceparent``), so that the server continues it. Only
the API is used: where nobody set OpenTelemetry up and no trace arrived, nothing is added.
"""

from opentelemetry import propagate


def traced(headers: dict[str, str]) -> dict[str, str]:
    """``headers``, with the running trace beside them (unchanged outside of one)."""
    carried = dict(headers)
    propagate.inject(carried)
    return carried
