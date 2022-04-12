from typing import Dict
from pydantic import BaseModel
from rath.operation import Operation
from rath.links.parsing import ParsingLink


def parse_variables(
    variables: Dict,
) -> Dict:
    def recurse_extract(path, obj):
        """
        recursively traverse obj, doing a deepcopy, but
        replacing any file-like objects with nulls and
        shunting the originals off to the side.
        """

        if isinstance(obj, list):
            nulled_obj = []
            for key, value in enumerate(obj):
                value = recurse_extract(f"{path}.{key}", value)
                nulled_obj.append(value)
            return nulled_obj
        elif isinstance(obj, dict):
            nulled_obj = {}
            for key, value in obj.items():
                value = recurse_extract(f"{path}.{key}", value)
                nulled_obj[key] = value
            return nulled_obj
        elif isinstance(obj, BaseModel):
            return obj.dict(by_alias=True)
        else:
            # base case: pass through unchanged
            return obj

    dicted_variables = recurse_extract("variables", variables)

    return dicted_variables


class DictingLink(ParsingLink):
    async def aparse(self, operation: Operation) -> Operation:
        shrinked_variables = parse_variables(operation.variables)
        operation.variables.update(shrinked_variables)
        return operation
