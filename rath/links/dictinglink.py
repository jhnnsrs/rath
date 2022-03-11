from pydantic import BaseModel
from rath.operation import Operation
from rath.links.parsing import ParsingLink


class DictingLink(ParsingLink):
    def parse(self, operation: Operation) -> Operation:
        shrinked_variables = {
            key: var.dict()
            for key, var in operation.variables.items()
            if isinstance(var, BaseModel)
        }
        operation.variables.update(shrinked_variables)
        return operation

    async def aparse(self, operation: Operation) -> Operation:
        shrinked_variables = {
            key: var.dict()
            for key, var in operation.variables.items()
            if isinstance(var, BaseModel)
        }
        operation.variables.update(shrinked_variables)
        return operation
