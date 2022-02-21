---
sidebar_label: rath
title: rath
---

## Rath Objects

```python
class Rath()
```

#### \_\_init\_\_

```python
def __init__(link: TerminatingLink, register=False, autoconnect=True) -> None
```

Initialize a Rath client

Rath takes a instance of TerminatingLink and creates an interface around it
to enable easy usage of the GraphQL API.

**Arguments**:

- `link` _TerminatingLink_ - A terminating link or a composed link.
- `register` _bool, optional_ - Register as a global rath (knowing the risks). Defaults to False.
- `autoconnect` _bool, optional_ - [description]. Defaults to True.

