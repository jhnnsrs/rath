# rath

[![codecov](https://codecov.io/gh/jhnnsrs/rath/branch/master/graph/badge.svg?token=UGXEA2THBV)](https://codecov.io/gh/jhnnsrs/rath)
[![PyPI version](https://badge.fury.io/py/rath.svg)](https://pypi.org/project/rath/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://pypi.org/project/rath/)
![Maintainer](https://img.shields.io/badge/maintainer-jhnnsrs-blue)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/rath.svg)](https://pypi.python.org/pypi/rath/)
[![PyPI status](https://img.shields.io/pypi/status/rath.svg)](https://pypi.python.org/pypi/rath/)
[![PyPI download month](https://img.shields.io/pypi/dm/rath.svg)](https://pypi.python.org/pypi/rath/)

### BETA

## Inspiration

Rath is a transportation agnostic graphql client for python focused on composability. It utilizes Links to
compose GraphQL request logic, similar to the apollo client in typescript. It comes with predefined links to
enable transports like aiohttp, websockets and httpx, as well as links to retrieve auth tokens, enable retry logic
or validating requests on a schema.

## Supported Transports

- aiohttp
- httpx
- websockets

## Installation

```bash
pip install rath
```

## Usage Example

```python
from rath.links.auth import AuthTokenLink
from rath.links.aiohttp import AIOHttpLink
from rath.links import compose, split
from rath.gql import gql

async def aload_token():
    return "SERVER_TOKEN"


auth = AuthTokenLink(token_loader=aload_token)
link = AIOHttpLink(endpoint_url="https://api.spacex.land/graphql/")


with Rath(links=compose(auth,link)) as rath:
    query = """query TestQuery {
      capsules {
        id
        missions {
          flight
        }
      }
    }
    """

    result = rath.query(query)
```

This example composes both the AuthToken and AioHttp link: During each query the Bearer headers are set to the retrieved token, on authentication fail (for example if Token Expired) the AuthToken automatically refetches the token and retries the query.

## Async Usage

Rath is build for async usage but uses koil, for async/sync compatibility

```python
from rath.links.auth import AuthTokenLink
from rath.links.aiohttp import AIOHttpLink
from rath.links import compose, split
from rath.gql import gql

async def aload_token():
    return "SERVER_TOKEN"


auth = AuthTokenLink(token_loader=aload_token)
link = AIOHttpLink(endpoint_url="https://api.spacex.land/graphql/")


async def main():

  async with Rath(links=compose(auth,link)) as rath:
      query = """query TestQuery {
        capsules {
          id
          missions {
            flight
          }
        }
      }
      """

      result = await rath.query(query)

asyncio.run(main())
```

## Example Transport Switch

Links allow the composition of additional logic based on your graphql operation. For example you might want
to use different grapqhl transports for different kind of operations (e.g using websockets for subscriptions,
but using standard http requests for potential caching on queries and mutations). This can be easily
accomplished by providing a split link.

```python
link = SplitLink(
  AioHttpLink(url="https://api.spacex.land/graphql/"),
  WebsocketLink(url="ws://api.spacex.land/graphql/",
  lambda o: o.node.operation == OperationType.SUBSCRIPTION
)

rath = Rath(link=link)

```

## Included Links

- Validating Link (validate query against local schema (or introspect the schema))
- Reconnecting WebsocketLink
- AioHttpLink (supports multipart uploads)
- SplitLink (allows to split the terminating link - Subscription into WebsocketLink, Query, Mutation into Aiohttp)
- AuthTokenLink (Token insertion with automatic refres

## Authentication

If you want to use rath with herre for getting access_tokens in oauth2/openid-connect scenarios, there is also a herre link
in this repository

### Why Rath

Well "apollo" is already taken as a name, and rath (according to wikipedia) is an etruscan deity identified with Apollo.

## Rath + Turms

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

## Examples

This github repository also contains an example client with a turms generated query with the public SpaceX api, as well as a sample of the generated api.
