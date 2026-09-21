---
sidebar_position: 5
sidebar_label: "Rath ❤️ Turms"
---

# Rath ❤️ Turms

### What is turms?

Turms is a graphql-codegen inspired code generator for python that generates fully typed and
serialized operations from your graphql schema. Just define your query in standard graphql syntax
and let turms create fully typed queries/mutation and subscriptions, that you can use in your favourite
IDE and with your favourite client like rath.

### Inspiration

Imaging you have a schema like this

```graphql title="schema.graphql"
type Beast {
  "ID of beast (taken from binomial initial)"
  id: ID
  "number of legs beast has"
  legs: Int
  "a beast's name in Latin"
  binomial: String
  "a beast's name to you and I"
  commonName: String
  "taxonomy grouping"
  taxClass: String
  "a beast's prey"
  eats: [Beast]
  "a beast's predators"
  isEatenBy: [Beast]
}

type Query {
  beasts: [Beast]
  beast(id: ID!): Beast
  calledBy(commonName: String!): [Beast]
}

type Mutation {
  createBeast(
    id: ID!
    legs: Int!
    binomial: String!
    commonName: String!
    taxClass: String!
    eats: [ID]
  ): Beast
}

type Subscription {
  watchBeast(id: ID!): Beast
}
```

And in your python code you would like to query all of the beasts

```graphql title="/graphql/test.graphql"
fragment Beast on Beast {
  commonName
  taxClass
}

query get_beasts {
  beasts {
    ...Beast
  }
}
```

In normal rath logic you would write the code something like this

```python

rath = Rath(AIOHttpLink(url="..."))

with rath:
    result = rath.execute("""
      fragment Beast on Beast {
      commonName
      taxClass
    }

    query get_beasts {
      beasts {
        ...Beast
      }
    }
    """)

    first_beast_name = result.data["get_beasts"][0]["commonName"]

```

This would be a perfectly fine scenario, however accessing nested dictionaries, can lead to unexpected
bugs when accessing by wrongly spelled keys and especially is hard to debug if there are ever changes to your api.
Wouldn't it be nice to have the type safety of graphql in your python code?

### Turms

Turms can generate pydantic models that are automatically validated through your schema and makes working with
graphql fragments and operations super easy.

Turms requires a graphl.config.yaml file to generate code, for this
example we can use the following:
```yaml
projects:
  default:
    schema: schema.graphql
    documents: graphql/**.graphql
    extensions:
      turms:
        out_dir: api
        stylers:
          - type: turms.stylers.capitalize.Capitalizer
        plugins:
          - type: turms.plugins.enums.EnumsPlugin
          - type: turms.plugins.fragments.FragmentsPlugin
          - type: turms.plugins.operations.OperationsPlugin
          - type: turms.plugins.funcs.FuncsPlugin
            global_kwargs:
              - key: rath
                type: rath.rath.Rath
                description: The rath client to execute the operation on
            definitions:
              - type: query
                use: rath.turms.funcs.execute
              - type: mutation
                use: rath.turms.funcs.execute
              - type: subscription
                use: rath.turms.funcs.subscribe
              - type: query
                is_async: true
                use: rath.turms.funcs.aexecute
              - type: mutation
                is_async: true
                use: rath.turms.funcs.aexecute
              - type: subscription
                is_async: true
                use: rath.turms.funcs.asubscribe
        scalar_definitions:
          uuid: str
```

Turms generates fully typed classes for enums, fragments and operations. The
funcs plugin adds a function per operation on top of them -- a sync one and an
`a`-prefixed async one -- and `definitions` is where you say what those
functions should call. Here that is `rath.turms.funcs`, which knows how to run
an operation on a rath; `global_kwargs` is what puts the `rath=` parameter on
every generated function.

This is rath's own configuration, near enough: the real one lives in
`graphql.config.yaml` at the repo root and generates `tests/apis/`.

On running (in your terminal)

```bash
turms gen
```

Turms generates automatically this pydantic schema for you

```python title="api/schema.py"
from pydantic import BaseModel, Field
from rath.rath import Rath
from rath.turms.funcs import aexecute, execute
from typing import Any, Literal


class Beast(BaseModel):
    """No documentation"""

    typename: Literal["Beast"] = Field(alias="__typename", default="Beast")
    common_name: str | None = Field(default=None, alias="commonName")
    "a beast's name to you and I"
    tax_class: str | None = Field(default=None, alias="taxClass")
    "taxonomy grouping"

    class Meta:
        """Meta class for Beast"""

        document = "fragment Beast on Beast {\n  commonName\n  taxClass\n  __typename\n}"
        name = "Beast"
        type = "Beast"


class Get_beasts(BaseModel):
    """No documentation found for this operation."""

    beasts: list[Beast | None] | None = Field(default=None)

    class Arguments(BaseModel):
        """Arguments for get_beasts"""

        pass

    class Meta:
        """Meta class for get_beasts"""

        document = "fragment Beast on Beast {\n  commonName\n  taxClass\n  __typename\n}\n\nquery get_beasts {\n  beasts {\n    ...Beast\n    __typename\n  }\n}"


def get_beasts(rath: Rath | None = None) -> list[Beast | None] | None:
    """get_beasts


    Args:
        rath (rath.rath.Rath): The rath client to execute the operation on

    Returns:
        list[Beast | None] | None
    """
    variables: dict[str, Any] = {}
    return execute(Get_beasts, variables, rath=rath).beasts


async def aget_beasts(rath: Rath | None = None) -> list[Beast | None] | None:
    """get_beasts


    Args:
        rath (rath.rath.Rath): The rath client to execute the operation on

    Returns:
        list[Beast | None] | None
    """
    variables: dict[str, Any] = {}
    return (await aexecute(Get_beasts, variables, rath=rath)).beasts
```

Which you can then use easily in your application code, like this

```python
from rath import Rath
from rath.links.aiohttp import AIOHttpLink
from api import get_beasts

rath = Rath(link=AIOHttpLink(endpoint_url="..."))

with rath:
    beasts = get_beasts(rath=rath)
    first_beast_name = beasts[0].common_name
```

Your queries are now strongly typed, with comments from your schema.

:::info
`rath.turms.funcs` is a thin adapter between turms' funcs plugin and a rath --
four functions, one per operation type and asyncness. If you want the generated
code to go somewhere else, point `definitions` at your own module instead.
:::
