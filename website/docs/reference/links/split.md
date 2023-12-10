---
sidebar_label: split
title: links.split
---

## SplitLink Objects

```python
class SplitLink(TerminatingLink)
```

SplitLink is a link that splits the operation into two paths. The operation is sent to the left path if the predicate returns true, otherwise to the right path.

This is useful for exampole when implementing a cache link, where the operation is sent to the cache if it is a query, and to the network if it is a mutation.
Or when subscriptions and queries are sent to different links (e.g. a websocket link and a http link).

#### left

The link that is used if the predicate returns true.

#### right

The link that is used if the predicate returns false.

#### split

The function used to split the operation. This function should return a boolean. If true, the operation is sent to the left path, otherwise to the right path.

#### split

```python
def split(left: TerminatingLink, right: TerminatingLink,
          split: Callable[[Operation], bool])
```

Splits a Link into two paths. Acording to a predicate function. If predicate returns
true, the operation is sent to the left path, otherwise to the right path.

