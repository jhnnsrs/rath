from typing import Any, List


class NotQueriedError(Exception):
    pass


def get_nested_error(obj: Any, nested: List[str], above: List[str]) -> Any:
    """Get a nested attribute or raise an error


    Raises an error if a nested attribut is not present

    This is used to raise an error if a nested attribute is not present.
    And to give a hint where in a query tree a the nested attribute is missing.

    Parameters
    ----------
    obj : Any
        The object to query
    nested : List[str]
        The nested attributes to query
    above : _type_
        The attributes above the nested attribute ( will be filled by the function)

    Returns
    -------
    Any
        The queried object

    Raises
    ------
    NotQueriedError
        The nested attribute was not queried
    """
    if hasattr(obj, nested[0]):
        obj = getattr(obj, nested[0])
        if len(nested) > 1:
            return get_nested_error(obj, nested[1:], above + [nested[0]])
        else:
            return obj
    else:
        raise NotQueriedError(f"{nested} not queried. {above} was queried")


def get_attributes_or_error(self, *args) -> Any:
    """Get attributes or raise an error"""
    returns = []
    errors = []
    for i in args:
        if "." in i:
            try:
                returns.append(get_nested_error(self, i.split("."), []))
                continue
            except NotQueriedError:
                errors.append(i)
        else:
            if hasattr(self, i):
                returns.append(getattr(self, i))
            else:
                errors.append(i)

    if len(errors) > 0:
        raise NotQueriedError(
            f"Required fields {errors} not queried on {self.__class__.__name__}"
        )

    if len(args) == 1:
        return returns[0]
    else:
        return tuple(returns)
