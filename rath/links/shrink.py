from rath.operation import Operation
from rath.links.parsing import ParsingLink


class ShrinkingLink(ParsingLink):
    """Shrinking Link is a link that shrinks operation variables.
    It traverses the variables dict, and converts any model that has a .ashrink() method to its id.
    """

    async def aparse(self, operation: Operation) -> Operation:
        """Parses an operation

        This method will traverse the variables dict, and convert any model that has a .ashrink() method to its id.
        This is a helper method that can be used to shrink the variables of an operation before sending it to the server.
        (Utilized in the arkitekt framework)
        """

        shrinked_variables = {
            key: await var.ashrink()
            for key, var in operation.variables.items()
            if hasattr(var, "ashrink")
        }
        operation.variables.update(shrinked_variables)
        return operation
