---
sidebar_label: errors
title: links.errors
---

## LinkError Objects

```python
class LinkError(RathException)
```

Base class for all link errors.

## LinkNotConnectedError Objects

```python
class LinkNotConnectedError(LinkError)
```

LinkNotConnectedError is raised when the link is not connected and autoload is set to false.

## TerminatingLinkError Objects

```python
class TerminatingLinkError(LinkError)
```

Raised when a terminating link is called.

