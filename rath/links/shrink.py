from rath.links.utils import recurse_parse_variables
from rath.operation import Operation
from rath.links.parsing import ParsingLink


class ShrinkByID:
    id: str

    async def ashrink(self):
        return self.id

    def shrink(self):
        return self.id


class ShrinkingLink(ParsingLink):
    def parse(self, operation: Operation) -> Operation:
        shrinked_variables = recurse_parse_variables(
            operation.variables,
            predicate=lambda path, obj: hasattr(obj, "shrink"),
            apply=lambda obj: obj.shrink(),
        )
        operation.variables = shrinked_variables
        return operation

    async def aparse(self, operation: Operation) -> Operation:
        shrinked_variables = {
            key: await var.ashrink()
            for key, var in operation.variables.items()
            if hasattr(var, "ashrink")
        }
        operation.variables.update(shrinked_variables)
        return operation
