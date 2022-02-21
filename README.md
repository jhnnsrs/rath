# rath

[![codecov](https://codecov.io/gh/jhnnsrs/rath/branch/master/graph/badge.svg?token=UGXEA2THBV)](https://codecov.io/gh/jhnnsrs/rath)
[![PyPI version](https://badge.fury.io/py/rath.svg)](https://pypi.org/project/rath/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://pypi.org/project/rath/)
![Maintainer](https://img.shields.io/badge/maintainer-jhnnsrs-blue)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/rath.svg)](https://pypi.python.org/pypi/rath/)
[![PyPI status](https://img.shields.io/pypi/status/rath.svg)](https://pypi.python.org/pypi/rath/)
[![PyPI download month](https://img.shields.io/pypi/dm/rath.svg)](https://pypi.python.org/pypi/rath/)

### DEVELOPMENT

## Inspiration

Rath is like Apollo, but for python. It adheres to the design principle of Links and enables complex GraphQL
setups, like seperation of query and subscription endpoints, dynamic token loading, etc..

## Installation

```bash
pip install rath
```

## Usage Example

```python
from rath.links.auth import AuthTokenLink
from rath.links.aiohttp import AioHttpLink
from rath.links import compose, split
from rath.gql import gql

async def aload_token():
    return "SERVER_TOKEN"


auth = AuthTokenLink(token_loader=aload_token)
link = AioHttpLink(url="https://api.spacex.land/graphql/")


rath = Rath(links=compose(auth,link))
rath.connect()


query = """query TestQuery {
  capsules {
    id
    missions {
      flight
    }
  }
}
"""

result = rath.execute(query)
```

This example composes both the AuthToken and AioHttp link: During each query the Bearer headers are set to the retrieved token, on authentication fail (for example if Token Expired) the
AuthToken automatically refetches the token and retries the query.

## Async Usage

Rath is build with koil, for async/sync compatibility but also exposed a complete asynhronous api, also it is completely threadsafe

```python
from rath.links.auth import AuthTokenLink
from rath.links.aiohttp import AioHttpLink
from rath.links import compose, split
from rath.gql import gql

async def aload_token():
    return "SERVER_TOKEN"


auth = AuthTokenLink(token_loader=aload_token)
link = AioHttpLink(url="https://api.spacex.land/graphql/")


async def main():
  rath = Rath(links=compose(auth,link))
  await rath.aconnect()


  query = """query TestQuery {
    capsules {
      id
      missions {
        flight
      }
    }
  }
  """

  result = await rath.aexecute(query)

asyncio.run(main())
```

## Usage of Async Links in Sync Environments

Links can either have a synchronous or asynchronous interface (inheriting from SyncLink or AsyncLink). Using an Async Link from a Sync
context however is not possible without switching context. For this purpose exist SwitchLinks that can either switch from sync to async
or back.

```python

upload_files = UploadFilesSyncLink(bucket="lala")
switch = SwitchAsyncLink()
link = AioHttpLink(url="https://api.spacex.land/graphql/")

rath = Rath(link=compose(upload_files, switch, link))

```

## Example Transport Switch

```python
link = SplitLink(
  AioHttpLink(url="https://api.spacex.land/graphql/"),
  WebsocketLink(url="ws://api.spacex.land/graphql/",
  lamda o: o.node.operation == OperationType.SUBSCRIPTION
)

rath = Rath(link=link)

```

## Included Links

- Validating Link (validate query against local schema (or introspect the schema))
- Reconnecting WebsocketLink
- AioHttpLink (supports multipart uploads)
- SplitLink (allows to split the terminating link - Subscription into WebsocketLink, Query, Mutation into Aiohttp)
- AuthTokenLink (Token insertion with automatic refresh)

## Dynamic Configuration

rath follows some design principles of fakts for asynchronous configuration retrieval, and provides some examplary links

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


RATH = Rath(
    link=link,
    register=True, # allows global access (singleton-antipattern, but rath has no state)
)


async def main():
    capsules = await aget_capsules() # fully typed pydantic powered dataclasses generated through turms
    print(capsules)


asyncio.run(main())

```

## Examples

This github repository also contains an example client with a turms generated query with the public SpaceX api, as well as a sample of the generated api.
