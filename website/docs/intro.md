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

## Initilization

```python
from rath.links.aiohttp import AioHttpLink

link = AioHttpLink(url="https://api.spacex.land/graphql/")


rath = Rath(link=link)

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
