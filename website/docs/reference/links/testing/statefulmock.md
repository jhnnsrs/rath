---
sidebar_label: statefulmock
title: links.testing.statefulmock
---

#### target\_from\_node

```python
def target_from_node(node: FieldNode) -> str
```

Extract the target aka. the aliased name from a FieldNode.

**Arguments**:

- `node` _FieldNode_ - A GraphQL FieldNode.
  

**Returns**:

- `str` - The target

## ConfigurationError Objects

```python
class ConfigurationError(TerminatingLinkError)
```

A Configuration Error

## AsyncStatefulMockLink Objects

```python
class AsyncStatefulMockLink(AsyncTerminatingLink)
```

A Stateful Mocklink

This is a mocklink that can be used to mock a GraphQL server.
You need to pass resolvers to the constructor.

In addition to AsyncMockLink this class also supports Subscription,
and has internal state that needs to be handled.

#### resolving

```python
async def resolving()
```

A coroutine that resolves the incoming operations in
an inifite Loop

**Raises**:

- `NotImplementedError` - If the operation is not supported (aka not implemented)

