---
sidebar_label: base
title: links.base
---

## Link Objects

```python
class Link(KoiledModel)
```

A Link is a class that can be used to send operations to a GraphQL API.
its main method is aexecute, which takes an operation and returns an
AsyncIterator of GraphQLResults.

Links can be composed to form a chain of links. The last link in the chain
is the terminating link, which is responsible for sending the operation to
the server.

#### aconnect

```python
async def aconnect()
```

A coroutine that is called when the link is connected.

#### adisconnect

```python
async def adisconnect()
```

A coroutine that is called when the link is disconnected.

#### aexecute

```python
def aexecute(operation: Operation, **kwargs) -> AsyncIterator[GraphQLResult]
```

A coroutine that takes an operation and returns an AsyncIterator of GraphQLResults.
This method should be implemented by subclasses.

## TerminatingLink Objects

```python
class TerminatingLink(Link)
```

A TerminatingLink is a link that is responsible for sending the operation to the server.

The last link in a link chain MUST always a TerminatingLink. It cannot delegate the operation
to another link.

## AsyncTerminatingLink Objects

```python
class AsyncTerminatingLink(TerminatingLink)
```

An Async Termination Link

This is a link that terminates the query or subscription, aka
it is a link that does not have a next link. It normally
is used to make network requests with the already parsed
operations

**Arguments**:

- `TerminatingLink` __type__ - _description_

## ContinuationLink Objects

```python
class ContinuationLink(Link)
```

A ContinuationLink is a link that delegates the operation to the next link in the chain.
It can be either provided a next link or it can be set once the link is composed together

#### next

The next link in the chain. This is also set when the link is composed together.

