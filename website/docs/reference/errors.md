---
sidebar_label: errors
title: errors
---

## RathException Objects

```python
class RathException(Exception)
```

RathException is the base exception for all Rath errors.

## NotConnectedError Objects

```python
class NotConnectedError(RathException)
```

NotConnectedError is raised when the Rath is not connected and autoload is set to false.

## NotEnteredError Objects

```python
class NotEnteredError(RathException)
```

NotEnteredError is raised when the Rath is not entered and access to protected methods is attempted.

