---
sidebar_label: compose
title: links.compose
---

## ComposedLink Objects

```python
class ComposedLink(TerminatingLink)
```

A composed link is a link that is composed of multiple links. The links
are executed in the order they are passed to the constructor.

The first link in the chain is the first link that is executed. The last
link in the chain is the terminating link, which is responsible for sending
the operation to the server.

#### links

The links that are composed to form the chain. pydantic will validate that the last link is a terminating link.

## TypedComposedLink Objects

```python
class TypedComposedLink(TerminatingLink)
```

A typed composed link is a base class to create a definition for
a composed link. It is a link that is composed of multiple links that
will be set at compile time and not at runtime. Just add links
that you want to use to the class definition and they will be
automatically composed together.

#### compose

```python
def compose(*links: Link) -> ComposedLink
```

Compose a chain of links together. The first link in the chain is the first link that is executed.
The last link in the chain is the terminating link, which is responsible for sending the operation to the server.


**Returns**:

- `ComposedLink` - The composed link

