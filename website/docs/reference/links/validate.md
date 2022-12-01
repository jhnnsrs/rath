---
sidebar_label: validate
title: links.validate
---

## ValidatingLink Objects

```python
class ValidatingLink(ContinuationLink)
```

ValidatingLink validates the operation againt as schema before passing it on to the next link.

The schema can be provided as a dsl string, or as a glob to a set of graphql files.
If the schema is not provided, the link will introspect the server to get the schema if allow_introspection is set to True.

#### schema\_dsl

The schema (as a string) to validate against. If not provided, the link will introspect the server to get the schema if allow_introspection is set to True.

#### schema\_glob

The glob to a set of graphql files to validate against. If not provided, the link will introspect the server to get the schema if allow_introspection is set to True.

#### allow\_introspection

If set to True, the link will introspect the server to get the schema if it is not provided.

#### graphql\_schema

The schema to validate against. If not provided, the link will introspect the server to get the schema if allow_introspection is set to True.

