---
sidebar_label: split
title: links.split
---

#### split

```python
def split(left: TerminatingLink, right: TerminatingLink, split: Callable[[Operation], bool])
```

Splits a Link into two paths. Acording to a predicate function. If predicate returns
true, the operation is sent to the left path, otherwise to the right path.

