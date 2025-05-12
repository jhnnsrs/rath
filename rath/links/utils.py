from typing import Dict, Any, Callable, Optional


def recurse_parse_variables(
    variables: Dict[str, Any],
    predicate: Callable[[Optional[str], Any], bool],
    apply: Callable[[Any], Any],
) -> Dict[str, Any]:
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
            for key, value in enumerate(obj):  # type: ignore
                value = recurse_extract(
                    value,
                    path=f"{path}.{key}" if path else str(key),
                )
                nulled_list.append(value)  # type: ignore
            return nulled_list  # type: ignore
        elif isinstance(obj, dict):
            nulled_obj = {}
            for key, value in obj.items():  # type: ignore
                value = recurse_extract(value, f"{path}.{key}" if path else str(key))  # type: ignore
                nulled_obj[key] = value
            return nulled_obj  # type: ignore
        elif predicate(path, obj):
            return apply(obj)
        else:
            return obj

    dicted_variables = recurse_extract(variables)

    return dicted_variables
