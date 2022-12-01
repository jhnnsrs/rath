---
sidebar_label: shrink
title: links.shrink
---

## ShrinkingLink Objects

```python
class ShrinkingLink(ParsingLink)
```

Shrinking Link is a link that shrinks operation variables.
It traverses the variables dict, and converts any model that has a .ashrink() method to its id.

