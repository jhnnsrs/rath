# rath

[![codecov](https://codecov.io/gh/jhnnsrs/rath/branch/master/graph/badge.svg?token=UGXEA2THBV)](https://codecov.io/gh/jhnnsrs/rath)
[![PyPI version](https://badge.fury.io/py/rath.svg)](https://pypi.org/project/rath/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://pypi.org/project/rath/)
![Maintainer](https://img.shields.io/badge/maintainer-jhnnsrs-blue)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/rath.svg)](https://pypi.python.org/pypi/rath/)
[![PyPI status](https://img.shields.io/pypi/status/rath.svg)](https://pypi.python.org/pypi/rath/)
[![PyPI download month](https://img.shields.io/pypi/dm/rath.svg)](https://pypi.python.org/pypi/rath/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/jhnnsrs/rath)



## Inspiration

Rath is a transportation agnostic graphql client for python focused on composability. It utilizes `Links` to
compose GraphQL request logic, similar to the apollo client in typescript. It comes with predefined links to
enable transports like aiohttp, websockets and httpx, as well as links to retrieve auth tokens, enable retry logic
or validating requests on a schema.

## Supported Transports

- aiohttp
- httpx
- websockets (both  graphql-ws and subscriptions-transport-ws)

## Installation

```bash
pip install rath
```

## Usage Example

```python
from rath.links.auth import ComposedAuthLink
from rath.links.aiohttp import AIOHttpLink
from rath.links import compose
from rath import Rath

async def aload_token():
    return "SERVER_TOKEN"


auth = ComposedAuthLink(token_loader=aload_token)
link = AIOHttpLink(endpoint_url="https://countries.trevorblades.com/")


with Rath(link=compose(auth,link)) as rath:
    query = """query {
        countries {
            native
            capital
        }
        }

    """

    result = rath.query(query)
    print(result)
```

This example composes both the AuthToken and AIOHttp link: During each query the Bearer headers are set to the retrieved token, and the query is sent to the specified endpoint.
(Additionally if the servers raises a 401, the token is refreshed and the query is retried)


## Async Usage

Rath is build for async usage but uses koil, for async/sync compatibility

```python
from rath.links.auth import ComposedAuthLink
from rath.links.aiohttp import AIOHttpLink
from rath.links import compose
from rath import Rath

async def aload_token():
    return "SERVER_TOKEN"


auth = ComposedAuthLink(token_loader=aload_token)
link = AIOHttpLink(endpoint_url="https://countries.trevorblades.com/")

async def main():

  async with Rath(link=compose(auth,link)) as rath:
      query = """query {
          countries {
              native
              capital
          }
          }

      """

      result = await rath.aquery(query)
      print(result)


asyncio.run(main())
```

## Example Transport Switch

Links allow the composition of additional logic based on your graphql operation. For example you might want
to use different grapqhl transports for different kind of operations (e.g using websockets for subscriptions,
but using standard http requests for potential caching on queries and mutations). This can be easily
accomplished by providing a split link.

```python
from rath.links.auth import ComposedAuthLink
from rath.links.aiohttp import AIOHttpLink
from rath.links.graphql_ws import GraphQLWSLink
from rath.links import compose, split

from rath import Rath

async def aload_token():
    return "SERVER_TOKEN"


auth = ComposedAuthLink(token_loader=aload_token)
link = AIOHttpLink(endpoint_url="https://countries.trevorblades.com/")
ws = GraphQLWSLink(ws_endpoint_url="wss://countries.trevorblades.com/") # 


end_link = split(link, ws, lambda op: op.node.operation != "subscription")


with Rath(link=end_link) as rath:
    query = """query {
        countries {
            native
            capital
        }
        }

    """

    result = rath.query(query) # uses the http link
    print(result)

    subscription = """subscription {
        newCountry {
            native
            capital
        }
        }

    """

    for i in rath.subscribe(subscription): # uses the ws link
        print(i) # will fail because the server does not support subscriptions

  
```

## Included Links

- Validating Link (validate query against local schema (or introspect the schema))
- Reconnecting WebsocketLink
- AioHttpLink (with multi-part upload support)
- SplitLink (allows to split the terminating link - Subscription into WebsocketLink, Query, Mutation into Aiohttp)
- AuthTokenLink (Token insertion with automatic refreshs)


## Typed Operations

Searching for a solution to generate typed operations for your graphql api? Look no further, rath + turms has you covered. [Turms](https://github.com/jhnnsrs/turms) is a graphql code generator that allows you to generate typed operations for your graphql api.

Rath works especially well with turms generated typed operations:

```python
import asyncio
from examples.api.schema import aget_capsules
from rath.rath import Rath
from rath.links.aiohttp import AIOHttpLink
from rath.links.auth import AuthTokenLink
from rath.links.compose import compose


async def token_loader():
    return ""


link = compose(
    AuthTokenLink(token_loader), AIOHttpLink("https://api.spacex.land/graphql/")
)


rath = Rath(
    link=link,
    register=True, # allows global access (singleton-antipattern, but rath has no state)
)


async def main():

    async with rath:
        capsules = await aget_capsules() # fully typed pydantic powered dataclasses generated through turms
        print(capsules)


asyncio.run(main())

```

This github repository also contains an example client with a turms generated query with the public SpaceX api, as well as a sample of the generated api.
