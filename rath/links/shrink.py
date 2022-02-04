from rath.operation import Operation
from rath.links.parsing import ParsingLink


class ShrinkingLink(ParsingLink):
    def parse(self, operation: Operation) -> Operation:
        shrinked_variables = {
            key: var.shrink()
            for key, var in operation.variables.items()
            if hasattr(var, "shrink")
        }
        operation.variables.update(shrinked_variables)
        return operation

    async def aparse(self, operation: Operation) -> Operation:
        shrinked_variables = {
            key: await var.ashrink()
            for key, var in operation.variables.items()
            if hasattr(var, "shrink")
        }
        operation.variables.update(shrinked_variables)
        return operation
