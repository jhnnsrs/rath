import json
from typing import Dict
from pydantic import BaseModel
from rath.operation import Operation
from rath.links.parsing import ParsingLink


def parse_variables(
    variables: Dict,
    by_alias: bool = True,
) -> Dict:
    def recurse_extract(obj):
        """
        recursively traverse obj, doing a deepcopy, but
        replacing any  pydantic BaseModels with their dict representation
        """

        if isinstance(obj, list):
            nulled_obj = []
            for key, value in enumerate(obj):
                value = recurse_extract(value)
                nulled_obj.append(value)
            return nulled_obj
        elif isinstance(obj, dict):
            nulled_obj = {}
            for key, value in obj.items():
                value = recurse_extract(value)
                nulled_obj[key] = value
            return nulled_obj
        elif isinstance(obj, BaseModel):
            return json.loads(obj.json(by_alias=by_alias))
        else:
            # base case: pass through unchanged
            return obj

    dicted_variables = recurse_extract(variables)

    return dicted_variables


class DictingLink(ParsingLink):
    """Dicting Link is a link that converts pydantic models to dicts.
    It traversed the variables dict, and converts any (nested) pydantic models to dicts
    by callind their .json() method."""
    by_alias = True
    """Converts pydantic models to dicts by calling their .json() method with by_alias=True"""
    



    async def aparse(self, operation: Operation) -> Operation:
        shrinked_variables = parse_variables(operation.variables, by_alias=self.by_alias)
        operation.variables.update(shrinked_variables)
        return operation
