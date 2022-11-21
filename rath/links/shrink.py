from rath.operation import Operation
from rath.links.parsing import ParsingLink


class ShrinkByID:
    id: str

    async def ashrink(self):
        return self.id

    def shrink(self):
        return self.id


class ShrinkingLink(ParsingLink):
    
    """Shrinking Link is a link that shrinks operation variables.
    It traverses the variables dict, and converts any model that has a .ashrink() method to its id."""

    async def aparse(self, operation: Operation) -> Operation:

        shrinked_variables = {
            key: await var.ashrink()
            for key, var in operation.variables.items()
            if hasattr(var, "ashrink")
        }
        operation.variables.update(shrinked_variables)
        return operation
