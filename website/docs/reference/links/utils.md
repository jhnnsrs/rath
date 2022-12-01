---
sidebar_label: utils
title: links.utils
---

#### recurse\_parse\_variables

```python
def recurse_parse_variables(variables: Dict, predicate: Callable[[str, Any],
                                                                 bool],
                            apply: Callable[[Any], Any]) -> Dict
```

Parse Variables

Recursively traverse variables, applying the apply function to the value if the predicate
returns True.

**Arguments**:

- `variables` _Dict_ - The dictionary to parse.
  predicate (Callable[[str, Any], bool]):The path this is in
- `apply` _Callable[[Any], Any]_ - _description_
  

**Returns**:

- `Dict` - _description_

#### recurse\_parse\_variables\_with\_operation

```python
def recurse_parse_variables_with_operation(
        variables: Dict, operation: Operation,
        predicate: Callable[[str, Any], bool], apply: Callable[[Any],
                                                               Any]) -> Dict
```

Parse Variables

Recursively traverse variables, applying the apply function to the value if the predicate
returns True.

**Arguments**:

- `variables` _Dict_ - The dictionary to parse.
- `predicate` _Callable[[str, Any], bool]_ - _description_
- `apply` _Callable[[Any], Any]_ - _description_
  

**Returns**:

- `Dict` - _description_

