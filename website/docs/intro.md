---
sidebar_position: 1
sidebar_label: "Introduction"
---

# Quick Start

Let's discover **Rath in less than 5 minutes**.

### Inspiration

Rath is like Apollo, but for python. It adheres to the design principle of Links and enables complex GraphQL
setups, like seperation of query and subscription endpoints, dynamic token loading, etc.., but its also super easy to
configure and extendable

### Installation

```bash
pip install rath
```

### Design

Rath provides async and sync interfaces to support both programming paradigms, no matter which transport you are using.
This allow for example for synchronous iteration of websockets subscriptions. The prefered way of using rath is through
context managers, so that clean up code (like closing websocket connections), can be handled automatically.

```python
from rath.links.aiohttp import AioHttpLink
from rath import Rath

link = AioHttpLink(url="https://api.spacex.land/graphql/")


rath = Rath(link=link)

with rath as r

  query = """query TestQuery {
    capsules {
      id
      missions {
        flight
      }
    }
  }
  """

  result = r.execute(query)

```

If you dont want to use a context manager you can also choose to
use the connect/disconnect methods:

```python
from rath.links.aiohttp import AioHttpLink
from rath import Rath

link = AioHttpLink(url="https://api.spacex.land/graphql/")


rath = Rath(link=link)
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


# later
rath.disconnect()

```

:::warning
If you choose this approach, make sure that you call disconnect in your code at some
stage. Especially when using asynchronous links/transports (supporting subscriptions) in a sync
environment,as only on disconnect we will close the threaded loop that these transports required
to operate. Otherwise this connection will stay open.
:::

This is the same within an asyncio loop:

```python
from rath.links.aiohttp import AIOHttpLink
from rath import Rath
import asyncio

link = AioHttpLink(url="https://api.spacex.land/graphql/")
rath = Rath(link=link)


async def main():
  async with rath as r:

    query = """query TestQuery {
      capsules {
        id
        missions {
          flight
        }
      }
    }
    """

    result = await r.aexecute(query)


asyncio.run(main())
```

:::info

In this scenario we are using the asyncio event loop and do not spawn a seperate thread.

:::
