---
sidebar_label: dictinglink
title: links.dictinglink
---

## DictingLink Objects

```python
class DictingLink(ParsingLink)
```

Dicting Link is a link that converts pydantic models to dicts.
It traversed the variables dict, and converts any (nested) pydantic models to dicts
by callind their .json() method.

#### by\_alias

Converts pydantic models to dicts by calling their .json() method with by_alias=True

