---
sidebar_label: transpile
title: links.transpile
---

## TranspileHandler Objects

```python
class TranspileHandler(BaseModel)
```

A Transpilation Handler

A TranspileHandler is a function that takes any Any and returns a
GraphQLType. It is used to implement custom type resolution.

The default TranspileHandler is the identity function, which returns the
type passed to it.

## ListTranspileHandler Objects

```python
class ListTranspileHandler(BaseModel)
```

A List Transpile Handler

Similar to a TranspileHandler, but takes act on GraphqQLList Type of that type

## TranspilationError Objects

```python
class TranspilationError(Exception)
```

A transpilation Exception

## TranspilationHandlerException Objects

```python
class TranspilationHandlerException(TranspilationError)
```

A transpilation Exception happening within a TranspileHandler

## TranspileRegistry Objects

```python
class TranspileRegistry(BaseModel)
```

A Registry to hold TranspileHandlers

#### register\_item

```python
def register_item(graphql_type: str,
                  predicate: Callable[[Any], bool],
                  name=None)
```

A Decorator for registering a TranspileHandler

If acting on a List of this type, the handle_list parameter should be set to True.

**Example**:

  ```python
  registry = TranspileRegistry()
  
  @registry.register_item(&quot;ID&quot;, lambda x: isinstance(x, BaseModel))
  def transpile_id_to_id(x):
  return str(x.id)
  ```
  
  

**Arguments**:

- `graphql_type` _str_ - The graphql Type to act upon
- `predicate` _Callable[[Any], bool]_ - A predicate Function
- `name` __type_, optional_ - A name for this hanlder. Defaults to the function name.

#### register\_list

```python
def register_list(graphql_type: str,
                  predicate: Callable[[Any, str], bool],
                  name=None)
```

A Decorator for registering a TranspileHandler

If acting on a List of this type, the handle_list parameter should be set to True.

**Example**:

  ```python
  registry = TranspileRegistry()
  
  @registry.register_list(&quot;InputVector&quot;, lambda x, listdepth: isinstance(x, np.ndarray))
  def transpile_numpy_array_to_vectors(x, listdepth):
  assert listdepth == 1, &quot;Only one level of nesting is supported&quot;
  return [InputVector(x) for x in x]
  ```

**Arguments**:

- `graphql_type` _str_ - The graphql Type to act upon
- `predicate` _Callable[[Any], bool]_ - A predicate Function
- `handle_list` _bool, optional_ - Should we act on lists of this type. Defaults to False.
- `name` __type_, optional_ - A name for this hanlder. Defaults to the function name.

#### recurse\_transpile

```python
def recurse_transpile(key,
                      var: VariableNode,
                      value: Any,
                      registry: TranspileRegistry,
                      in_list=0,
                      strict=False)
```

Recurse Transpile a variable according to a registry and
its definition

**Arguments**:

- `key` __type__ - The key of the variable
- `var` _VariableNode_ - The variable definition node correspoin to this variable
- `value` _Any_ - The to transpile valued
- `registry` _TranspileRegistry_ - The transpile registry to use
- `in_list` _bool, optional_ - Recursive Parameter. That will be set to the list depth. Defaults to False.
- `strict` _bool, optional_ - Should we error on predicate errors. Defaults to False.
  

**Raises**:

- `TranspilationError` - _description_
  

**Returns**:

- `Any` - The transpiled value or the original value if no handler matched

#### transpile

```python
def transpile(op: OperationDefinitionNode,
              variables: Dict[str, Any],
              registry: TranspileRegistry,
              strict=False) -> Dict[str, Any]
```

Transpile

Transpiles a operations variabels to a dictionary of variables, with
json serializable values according to a transpile registry.

**Arguments**:

- `op` _OperationDefinitionNode_ - The operation definition node,
- `registry` _TranspileRegistry_ - The registry
- `strict` _bool, optional_ - Should we fail if a handler predicate fails. Defaults to False.
  

**Returns**:

- `Dict` - The transpiled variables

## TranspileLink Objects

```python
class TranspileLink(ParsingLink)
```

Transpile Link

Transpile Link is a link that transpiles variables according to a transpile registry.


**Attributes**:

- `registry` _TranspileRegistry_ - The transpile registry to use
- `strict` _bool_ - Should we fail if a handler predicate fails. Defaults to False.

