from rath.operation import Operation
from rath.links.parsing import ParsingLink


class ShrinkByID:
    id: str

    async def ashrink(self):
        return self.id

    def shrink(self):
        return self.id


class ShrinkingLink(ParsingLink):
    async def aparse(self, operation: Operation) -> Operation:
        shrinked_variables = {
            key: await var.ashrink()
            for key, var in operation.variables.items()
            if hasattr(var, "ashrink")
        }
        operation.variables.update(shrinked_variables)
        return operation
