from rath.links.base import ContinuationLink
from rath.operation import GraphQLResult, Operation
from typing import Any, AsyncIterator, Awaitable, Callable, Dict, Tuple, Type, Union
from rath.errors import NotComposedError
import asyncio


async def apply_recursive(
    func, obj, typeguard: Union[Type[Any], Tuple[Type[Any], ...]]
) -> Any:  # type: ignore
    """
    Recursively applies an asynchronous function to elements in a nested structure.

    Args:
        func (callable): The asynchronous function to apply.
        obj (any): The nested structure (dict, list, tuple, etc.) to process.
        typeguard (type): The type of elements to apply the function to.

    Returns:
        any: The nested structure with the function applied to elements of the specified type.
    """
    if isinstance(
        obj, dict
    ):  # If obj is a dictionary, recursively apply to each key-value pair
        return {k: await apply_recursive(func, v, typeguard) for k, v in obj.items()}  # type: ignore
    elif isinstance(obj, list):  # If obj is a list, recursively apply to each element
        return await asyncio.gather(
            *[apply_recursive(func, elem, typeguard) for elem in obj]
        )  # type: ignore
    elif isinstance(
        obj, tuple
    ):  # If obj is a tuple, recursively apply to each element and convert back to tuple
        return tuple(
            await asyncio.gather(
                *[apply_recursive(func, elem, typeguard) for elem in obj]
            )  # type: ignore
        )
    elif isinstance(obj, typeguard):
        return await func(obj)  # type: ignore
    else:  # If obj is not a dict, list, tuple, or matching the typeguard, return it as is
        return obj  # type: ignore


async def apply_typemap_recursive(
    obj, typefuncs: Dict[Type[Any], Callable[[Type[Any]], Awaitable[Any]]]
) -> Any:  # type: ignore
    """
    Recursively applies an asynchronous function to elements in a nested structure.

    Args:
        func (callable): The asynchronous function to apply.
        obj (any): The nested structure (dict, list, tuple, etc.) to process.
        typeguard (type): The type of elements to apply the function to.

    Returns:
        any: The nested structure with the function applied to elements of the specified type.
    """
    if isinstance(
        obj, dict
    ):  # If obj is a dictionary, recursively apply to each key-value pair
        return {k: await apply_typemap_recursive(v, typefuncs) for k, v in obj.items()}  # type: ignore
    elif isinstance(obj, list):  # If obj is a list, recursively apply to each element
        return await asyncio.gather(
            *[apply_typemap_recursive(elem, typefuncs) for elem in obj]
        )  # type: ignore
    elif isinstance(
        obj, tuple
    ):  # If obj is a tuple, recursively apply to each element and convert back to tuple
        return tuple(
            await asyncio.gather(
                *[apply_typemap_recursive(elem, typefuncs) for elem in obj]
            )  # type: ignore
        )
    else:
        applyer = typefuncs.get(type(obj), None)
        if applyer:
            return await applyer(obj)  # type: ignore
        else:
            return obj  # type: ignore


class ParsingLink(ContinuationLink):
    """ParsingLink is a link that parses operation and returns a new operation.
    It is an abstract class that needs to be implemented by the user.
    """

    async def aparse(self, operation: Operation) -> Operation:
        """Parses an operation

        This method needs to be implemented by the user.
        It should parse the operation and return a new operation.

        Parameters
        ----------
        operation : Operation
            The operation to execute

        Returns
        -------
        Operation
            The parsed operation
        """
        raise NotImplementedError("Please implement this method")

    async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
        """Executes an operation against the link

        This link will parse the operation and then forward it to the next link,
        the next link will then execute the operation.

        Parameters
        ----------
        operation : Operation
            The operation to execute

        Yields
        ------
        GraphQLResult
            The result of the operation
        """
        if not self.next:
            raise NotComposedError("No next link set")

        operation = await self.aparse(operation)
        async for result in self.next.aexecute(operation):
            yield result
