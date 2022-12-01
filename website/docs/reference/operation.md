---
sidebar_label: operation
title: operation
---

## Context Objects

```python
class Context(BaseModel)
```

Context provides a way to pass arbitrary data to resolvers on the context

## Extensions Objects

```python
class Extensions(BaseModel)
```

Extensions is a map of additional metadata that can be used by the links in the chain

## Operation Objects

```python
class Operation(BaseModel)
```

A GraphQL operation.

An Operation is a GraphQL operation that can be executed by a GraphQL client.
It is a combination of a query, variables, and headers, as well as a context
that can be used to pass additional information to the link chain and
extensions that can be used to pass additional information to the server.

## GraphQLResult Objects

```python
class GraphQLResult(BaseModel)
```

GraphQLResult is the result of a GraphQL operation.

## GraphQLException Objects

```python
class GraphQLException(Exception)
```

GraphQLException is the base exception for all GraphQL errors.

#### opify

```python
def opify(query: Union[str, DocumentNode],
          variables: Dict[str, Any] = None,
          headers: Dict[str, Any] = None,
          operation_name: Optional[str] = None,
          **kwargs) -> Operation
```

Opify takes a query, variables, and headers and returns an Operation.

**Arguments**:

- `query` _Union[str, DocumentNode]_ - The query string or the DocumentNode.
- `variables` _Dict[str, Any], optional_ - The variables. Defaults to None.
- `headers` _Dict[str, Any], optional_ - Additional headers. Defaults to None.
- `operation_name` _Optional[str], optional_ - The operation_name to be exceuted. Defaults to None.
  

**Returns**:

- `Operation` - A GraphQL operation

