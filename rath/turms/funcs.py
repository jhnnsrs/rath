from rath.rath import Rath
from collections.abc import Mapping
from typing import AsyncIterator, Iterator, Protocol, Type, TypeVar, Any, Optional
from pydantic import BaseModel


# --- Base meta description ---
class TurmsMeta(Protocol):
    """Meta class for Turms operations"""

    document: str


TArgs = TypeVar("TArgs", bound=BaseModel)
TMeta = TypeVar("TMeta", bound=TurmsMeta)


class TurmsOperation(Protocol[TArgs, TMeta]):
    """Represents a Turms operation that is both callable and its own return type."""

    Meta: Type[TMeta]
    Arguments: Type[TArgs]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """A pydantic constructor"""
        ...


TOperation = TypeVar("TOperation", bound=TurmsOperation[Any, Any])


def execute(operation: Type[TOperation], variables: Mapping[str, Any], rath: Rath) -> TOperation:
    """Synchronously Executes an a query or mutation using rath



    Parameters
    ----------
    operation : TurmsOperation
        The turms operation to execute
    variables : Mapping[str, Any]
        The variables to use
    rath : Rath
        The rath client to execute through

    Returns
    -------
    BaseModel
        The result of the operation
    """
    return operation(
        **rath.query(
            operation.Meta.document,
            operation.Arguments(**variables).model_dump(by_alias=True, exclude_unset=True),
        ).data
    )


async def aexecute(operation: Type[TOperation], variables: Mapping[str, Any], rath: Rath) -> TOperation:
    """Asynchronously Executes a query or mutation using rath



    Parameters
    ----------
    operation : TurmsOperation
        The turms operation to execute
    variables : Mapping[str, Any]
        The variables to use
    rath : Rath
        The rath client to execute through

    Returns
    -------
    BaseModel
        The result of the operation
    """
    x = await rath.aquery(
        operation.Meta.document,
        operation.Arguments(**variables).model_dump(by_alias=True, exclude_unset=True),
    )
    return operation(**x.data)


def subscribe(operation: Type[TOperation], variables: Mapping[str, Any], rath: Rath) -> Iterator[TOperation]:
    """Synchronously subscribte to a subscription using rath



    Parameters
    ----------
    operation : TurmsOperation
        The turms operation to execute
    variables : Mapping[str, Any]
        The variables to use
    rath : Rath
        The rath client to execute through

    Yields
    -------
    BaseModel
        The result of the operation
    """

    for event in rath.subscribe(
        operation.Meta.document,
        operation.Arguments(**variables).model_dump(by_alias=True, exclude_unset=True),
    ):
        yield operation(**event.data)


async def asubscribe(operation: Type[TOperation], variables: Mapping[str, Any], rath: Rath) -> AsyncIterator[TOperation]:
    """Asynchronously subscribte to a subscription using rath



    Parameters
    ----------
    operation : TurmsOperation
        The turms operation to execute
    variables : Mapping[str, Any]
        The variables to use
    rath : Rath
        The rath client to execute through

    yields
    -------
    BaseModel
        The result of the operation
    """

    async for event in rath.asubscribe(
        operation.Meta.document,
        operation.Arguments(**variables).model_dump(by_alias=True, exclude_unset=True),
    ):
        yield operation(**event.data)
