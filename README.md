# rath

[![codecov](https://codecov.io/gh/jhnnsrs/rath/branch/main/graph/badge.svg?token=UGXEA2THBV)](https://codecov.io/gh/jhnnsrs/rath)
[![PyPI version](https://badge.fury.io/py/rath.svg)](https://pypi.org/project/rath/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://pypi.org/project/rath/)
![Maintainer](https://img.shields.io/badge/maintainer-jhnnsrs-blue)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/rath.svg)](https://pypi.python.org/pypi/rath/)
[![PyPI status](https://img.shields.io/pypi/status/rath.svg)](https://pypi.python.org/pypi/rath/)
[![PyPI download month](https://img.shields.io/pypi/dm/rath.svg)](https://pypi.python.org/pypi/rath/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Rath is a **transport-agnostic GraphQL client for Python** focused on composability. Built on
[Pydantic v2](https://docs.pydantic.dev/) and [Koil](https://github.com/jhnnsrs/koil), it works
seamlessly in both async and sync code.

Inspired by Apollo Client, Rath composes request logic out of **links** — small, chainable
middleware objects that transform or forward an operation until a terminating link dispatches it
over the network. Need auth headers, retries, schema validation, persisted queries, or a websocket
transport for subscriptions? Each is just another link you drop into the chain.

## Features

- 🔌 **Pluggable transports** — aiohttp, httpx and websockets out of the box.
- 🧩 **Composable links** — build your request pipeline from small, reusable pieces.
- ⚡ **Async-first, sync-friendly** — call `aquery`/`asubscribe` from async code, or `query`/`subscribe` from sync code (powered by Koil).
- 🔐 **Auth with automatic refresh** — re-fetch the token and retry on a `401`/`403`.
- ✅ **Schema validation** — validate operations locally before they hit the wire.
- 🚀 **Automatic Persisted Queries (APQ)** — send a hash instead of the full document.
- 📦 **Typed operations** — pairs beautifully with [turms](https://github.com/jhnnsrs/turms) generated Pydantic models.
- 🧪 **First-class testing** — mock terminating links so unit tests never touch the network.

## Table of contents

- [Installation](#installation)
- [The link concept](#the-link-concept)
- [Quickstart](#quickstart)
- [Async usage](#async-usage)
- [Variables and headers](#variables-and-headers)
- [Handling errors](#handling-errors)
- [Authentication with refresh](#authentication-with-refresh)
- [Subscriptions and transport splitting](#subscriptions-and-transport-splitting)
- [Retries](#retries)
- [Timeouts](#timeouts)
- [Schema validation](#schema-validation)
- [Automatic Persisted Queries](#automatic-persisted-queries-apq)
- [Testing without a server](#testing-without-a-server)
- [Typed operations with turms](#typed-operations-with-turms)
- [Included links](#included-links)

## Installation

```bash
pip install rath
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add rath
```

## The link concept

A Rath client is configured with a single **terminating link** — the link that actually sends the
operation over the network (e.g. `AIOHttpLink`, `HttpxLink`, `GraphQLWSLink`).

To add behaviour, you wrap the terminating link with **continuation links** using `compose()`.
Operations flow left → right through the chain; results flow back right → left:

```
operation ─▶ AuthTokenLink ─▶ RetryLink ─▶ AIOHttpLink ─▶ server
result    ◀────────────────────────────────────────────◀
```

```python
from rath import Rath
from rath.links import compose
from rath.links.auth import ComposedAuthLink
from rath.links.retry import RetryLink
from rath.links.aiohttp import AIOHttpLink

link = compose(
    ComposedAuthLink(token_loader=...),   # add the Bearer header
    RetryLink(maximum_retry_attempts=3),  # retry on failure
    AIOHttpLink(endpoint_url="..."),      # terminating link
)

rath = Rath(link=link)
```

`Rath(link=...)` also accepts a plain list — it is composed for you, and the last element must be a
terminating link:

```python
rath = Rath(link=[auth, retry, AIOHttpLink(endpoint_url="...")])
```

## Quickstart

```python
from rath import Rath
from rath.links.aiohttp import AIOHttpLink

link = AIOHttpLink(endpoint_url="https://countries.trevorblades.com/")

with Rath(link=link) as rath:
    result = rath.query(
        """
        query {
            countries {
                native
                capital
            }
        }
        """
    )
    print(result.data)  # GraphQLResult — the payload lives on .data
```

## Async usage

Rath is built for async; the sync API above is just a thin wrapper. In async code use `aquery`,
`aquery_operation` and `asubscribe`:

```python
import asyncio
from rath import Rath
from rath.links.aiohttp import AIOHttpLink

link = AIOHttpLink(endpoint_url="https://countries.trevorblades.com/")


async def main():
    async with Rath(link=link) as rath:
        result = await rath.aquery(
            """
            query {
                countries {
                    native
                    capital
                }
            }
            """
        )
        print(result.data)


asyncio.run(main())
```

## Variables and headers

Pass `variables` and per-operation `headers` directly to `query`/`aquery`:

```python
with Rath(link=link) as rath:
    result = rath.query(
        """
        query Country($code: ID!) {
            country(code: $code) {
                name
                capital
            }
        }
        """,
        variables={"code": "DE"},
        headers={"X-Tenant": "acme"},
    )
    print(result.data["country"])
```

## Handling errors

When the server returns GraphQL errors, Rath raises a `GraphQLException` carrying the messages and
the offending operation:

```python
from rath.operation import GraphQLException

with Rath(link=link) as rath:
    try:
        result = rath.query("query { doesNotExist }")
    except GraphQLException as exc:
        print("GraphQL error:", exc.message)
        print("Operation:", exc.operation.operation_name)
```

## Authentication with refresh

`ComposedAuthLink` injects a `Bearer` token (returned by `token_loader`) into every request. If the
terminating link reports an authentication error (e.g. a `403`), the `token_refresher` is called and
the operation is retried — up to `maximum_refresh_attempts` times.

```python
from rath import Rath
from rath.links import compose
from rath.links.auth import ComposedAuthLink
from rath.links.aiohttp import AIOHttpLink


async def aload_token() -> str:
    return "SERVER_TOKEN"


async def arefresh_token() -> str:
    # e.g. exchange a refresh token for a fresh access token
    return "REFRESHED_TOKEN"


auth = ComposedAuthLink(token_loader=aload_token, token_refresher=arefresh_token)
http = AIOHttpLink(endpoint_url="https://countries.trevorblades.com/")

with Rath(link=compose(auth, http)) as rath:
    result = rath.query("query { countries { capital } }")
    print(result.data)
```

## Subscriptions and transport splitting

Different operation types often want different transports: websockets for subscriptions, plain HTTP
for queries and mutations (so they stay cacheable). `split` routes each operation to one of two
links based on a predicate.

```python
from graphql import OperationType
from rath import Rath
from rath.links import compose, split
from rath.links.auth import ComposedAuthLink
from rath.links.aiohttp import AIOHttpLink
from rath.links.graphql_ws import GraphQLWSLink


async def aload_token() -> str:
    return "SERVER_TOKEN"


auth = ComposedAuthLink(token_loader=aload_token)
http = AIOHttpLink(endpoint_url="https://api.example.com/graphql")
ws = GraphQLWSLink(ws_endpoint_url="wss://api.example.com/graphql")

# Predicate True  -> first link (http)
# Predicate False -> second link (ws)
transport = split(http, ws, lambda op: op.node.operation != OperationType.SUBSCRIPTION)

with Rath(link=compose(auth, transport)) as rath:
    # queries and mutations go over HTTP
    print(rath.query("query { countries { capital } }").data)

    # subscriptions go over the websocket link
    for event in rath.subscribe("subscription { newCountry { capital } }"):
        print(event.data)
```

> **Note:** `op.node.operation` is a graphql-core `OperationType` enum — compare against
> `OperationType.SUBSCRIPTION`, not the string `"subscription"`.

## Retries

`RetryLink` retries an operation when the terminating link fails (handy for flaky connections and
dropped subscriptions):

```python
from rath.links import compose
from rath.links.retry import RetryLink
from rath.links.aiohttp import AIOHttpLink

link = compose(
    RetryLink(maximum_retry_attempts=5, sleep_interval=1),  # wait 1s between attempts
    AIOHttpLink(endpoint_url="https://countries.trevorblades.com/"),
)
```

## Timeouts

`TimeoutLink` aborts an operation that takes longer than `timeout` seconds:

```python
from rath.links import compose
from rath.links.timeout import TimeoutLink
from rath.links.aiohttp import AIOHttpLink

link = compose(
    TimeoutLink(timeout=10),  # seconds
    AIOHttpLink(endpoint_url="https://countries.trevorblades.com/"),
)
```

## Schema validation

`ValidatingLink` validates each operation against a GraphQL schema *before* it is sent, so malformed
queries fail fast with a clear error. Provide the schema as a DSL string, a glob of `.graphql`
files, or let it introspect the remote schema.

```python
from rath.links import compose
from rath.links.validate import ValidatingLink
from rath.links.aiohttp import AIOHttpLink

link = compose(
    ValidatingLink(schema_glob="schemas/**/*.graphql"),
    AIOHttpLink(endpoint_url="https://countries.trevorblades.com/"),
)
```

## Automatic Persisted Queries (APQ)

`ApqLink` sends a SHA-256 hash of the query instead of the full document. If the server hasn't seen
the query yet it transparently retries with the full text. This shrinks request payloads and plays
well with CDN caching.

```python
from rath.links import compose
from rath.links.apq import ApqLink
from rath.links.aiohttp import AIOHttpLink

link = compose(
    ApqLink(),
    AIOHttpLink(endpoint_url="https://countries.trevorblades.com/"),
)
```

## Testing without a server

The `rath.links.testing` package provides terminating links that resolve operations locally, so unit
tests never hit the network. `AsyncMockLink` takes a dict of resolvers keyed by field name; each
resolver receives the `Operation` and returns the value for that field:

```python
from rath import Rath
from rath.links.testing.mock import AsyncMockLink
from rath.operation import Operation


async def resolve_countries(operation: Operation):
    return [{"capital": "Berlin", "native": "Deutschland"}]


link = AsyncMockLink(query_resolver={"countries": resolve_countries})

with Rath(link=link) as rath:
    result = rath.query("query { countries { native capital } }")
    assert result.data == {"countries": [{"capital": "Berlin", "native": "Deutschland"}]}
```

Use `AsyncStatefulMockLink` when you also need to mock subscriptions, and `AssertLink` together with
`compose()` to assert that upstream links transformed an operation as expected.

## Typed operations with turms

Looking for fully typed operations for your GraphQL API? Rath pairs with
[turms](https://github.com/jhnnsrs/turms), a code generator that turns your `.graphql` documents
into typed, Pydantic-powered functions:

```python
import asyncio
from examples.api.schema import aget_capsules  # turms-generated
from rath import Rath
from rath.links import compose
from rath.links.auth import ComposedAuthLink
from rath.links.aiohttp import AIOHttpLink


async def aload_token() -> str:
    return ""


rath = Rath(
    link=compose(
        ComposedAuthLink(token_loader=aload_token),
        AIOHttpLink(endpoint_url="https://api.spacex.land/graphql/"),
    ),
)


async def main():
    # Entering the client registers it as the current Rath, so turms-generated
    # functions can find it without passing the client explicitly.
    async with rath:
        capsules = await aget_capsules()  # fully typed result
        print(capsules)


asyncio.run(main())
```

This repository contains an example turms-generated client (`examples/`) querying the public SpaceX
API, plus a sample of the generated code.

## Included links

| Link | Purpose |
|------|---------|
| `AIOHttpLink` | HTTP transport via aiohttp (with multi-part file upload support) |
| `HttpxLink` | HTTP transport via httpx |
| `GraphQLWSLink` | WebSocket transport (`graphql-ws` protocol), with reconnection |
| `SubscriptionTransportWsLink` | Legacy `subscriptions-transport-ws` protocol |
| `SplitLink` (`split`) | Route operations to different terminating links by type |
| `ComposedAuthLink` / `AuthTokenLink` | Bearer-token insertion with automatic refresh |
| `RetryLink` | Retry failed operations with optional back-off |
| `TimeoutLink` | Abort operations that exceed a deadline |
| `ValidatingLink` | Validate operations against a schema before sending |
| `ApqLink` | Automatic Persisted Queries |
| `FileExtraction` | Extract (nested) file-like objects from variables for upload |
| Testing links | `AsyncMockLink`, `AsyncStatefulMockLink`, `AssertLink`, … |

## License

See [LICENSE](LICENSE).
