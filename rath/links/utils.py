from typing import Dict, Any, Callable, Optional

from rath.operation import Operation


def recurse_parse_variables(
    variables: Dict,
    predicate: Callable[[Optional[str], Any], bool],
    apply: Callable[[Any], Any],
) -> Dict:
    """Parse Variables

    Recursively traverse variables, applying the apply function to the value if the predicate
    returns True.

    Args:
        variables (Dict): The dictionary to parse.
        predicate (Callable[[str, Any], bool]):The path this is in
        apply (Callable[[Any], Any]): _description_

    Returns:
        Dict: _description_
    """

    def recurse_extract(obj: Any, path: Optional[str] = None) -> Any:
        """
        recursively traverse obj, doing a deepcopy, but
        replacing any file-like objects with nulls and
        shunting the originals off to the side.
        """

        if isinstance(obj, list):
            nulled_list = []
            for key, value in enumerate(obj):
                value = recurse_extract(
                    value,
                    path=f"{path}.{key}" if path else str(key),
                )
                nulled_list.append(value)
            return nulled_list
        elif isinstance(obj, dict):
            nulled_obj = {}
            for key, value in obj.items():
                value = recurse_extract(value, f"{path}.{key}" if path else str(key))
                nulled_obj[key] = value
            return nulled_obj
        elif predicate(path, obj):
            return apply(obj)
        else:
            return obj

    dicted_variables = recurse_extract(variables)

    return dicted_variables


def recurse_parse_variables_with_operation(
    variables: Dict,
    operation: Operation,
    predicate: Callable[[Optional[str], Any], bool],
    apply: Callable[[Any], Any],
) -> Dict:
    """Parse Variables

    Recursively traverse variables, applying the apply function to the value if the predicate
    returns True.

    Args:
        variables (Dict): The dictionary to parse.
        predicate (Callable[[str, Any], bool]): _description_
        apply (Callable[[Any], Any]): _description_

    Returns:
        Dict: _description_
    """

    def recurse_extract(obj: Any, path: Optional[str] = None) -> Any:
        """
        recursively traverse obj, doing a deepcopy, but
        replacing any file-like objects with nulls and
        shunting the originals off to the side.
        """

        if isinstance(obj, list):
            nulled_list = []
            for key, value in enumerate(obj):
                value = recurse_extract(
                    value,
                    path=f"{path}.{key}" if path else str(key),
                )
                nulled_list.append(value)
            return nulled_list
        elif isinstance(obj, dict):
            nulled_obj = {}
            for key, value in obj.items():
                value = recurse_extract(value, f"{path}.{key}" if path else str(key))
                nulled_obj[key] = value
            return nulled_obj
        elif predicate(path, obj):
            return apply(obj)
        else:
            return obj

    dicted_variables = recurse_extract(variables)

    return dicted_variables
