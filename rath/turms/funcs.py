from rath.rath import Rath, current_rath
from typing import AsyncIterator, Iterator, Protocol, Type, TypeVar, Any, Dict, Optional
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


def execute(operation: Type[TOperation], variables: Dict[str, Any], rath: Optional[Rath] = None) -> TOperation:
    """Synchronously Executes an a query or mutation using rath


    This function will execute an operation using rath, retrieving
    the currentliy active rath client from the current_rath context
    if no rath client is provided.

    Parameters
    ----------
    operation : TurmsOperation
        The turms operation to execute
    variables : Dict[str, Any]
        The variables to use
    rath : Optional[Rath], optional
        The rath client, by default the current rath client

    Returns
    -------
    BaseModel
        The result of the operation
    """
    rath = rath or current_rath.get()
    assert rath is not None, "No rath client provided and no rath client in current_rath context"
    return operation(
        **rath.query(
            operation.Meta.document,
            operation.Arguments(**variables).model_dump(by_alias=True),
        ).data
    )


async def aexecute(operation: Type[TOperation], variables: Dict[str, Any], rath: Optional[Rath] = None) -> TOperation:
    """Asynchronously Executes a query or mutation using rath


    This function will execute an operation using rath, retrieving
    the currentliy active rath client from the current_rath context
    if no rath client is provided.

    Parameters
    ----------
    operation : TurmsOperation
        The turms operation to execute
    variables : Dict[str, Any]
        The variables to use
    rath : Optional[Rath], optional
        The rath client, by default the current rath client

    Returns
    -------
    BaseModel
        The result of the operation
    """
    rath = rath or current_rath.get()
    assert rath is not None, "No rath client provided and no rath client in current_rath context"
    x = await rath.aquery(
        operation.Meta.document,
        operation.Arguments(**variables).model_dump(by_alias=True),
    )
    return operation(**x.data)


def subscribe(operation: Type[TOperation], variables: Dict[str, Any], rath: Optional[Rath] = None) -> Iterator[TOperation]:
    """Synchronously subscribte to a subscription using rath


    This function will execute an operation using rath, retrieving
    the currentliy active rath client from the current_rath context
    if no rath client is provided.

    Parameters
    ----------
    operation : TurmsOperation
        The turms operation to execute
    variables : Dict[str, Any]
        The variables to use
    rath : Optional[Rath], optional
        The rath client, by default the current rath client

    Yields
    -------
    BaseModel
        The result of the operation
    """
    rath = rath or current_rath.get()
    assert rath is not None, "No rath client provided and no rath client in current_rath context"

    for event in rath.subscribe(
        operation.Meta.document,
        operation.Arguments(**variables).model_dump(by_alias=True),
    ):
        yield operation(**event.data)


async def asubscribe(operation: Type[TOperation], variables: Dict[str, Any], rath: Optional[Rath] = None) -> AsyncIterator[TOperation]:
    """Asynchronously subscribte to a subscription using rath


    This function will execute an operation using rath, retrieving
    the currentliy active rath client from the current_rath context
    if no rath client is provided.

    Parameters
    ----------
    operation : TurmsOperation
        The turms operation to execute
    variables : Dict[str, Any]
        The variables to use
    rath : Optional[Rath], optional
        The rath client, by default the current rath client

    yields
    -------
    BaseModel
        The result of the operation
    """
    rath = rath or current_rath.get()
    assert rath is not None, "No rath client provided and no rath client in current_rath context"

    async for event in rath.asubscribe(
        operation.Meta.document,
        operation.Arguments(**variables).model_dump(by_alias=True),
    ):
        yield operation(**event.data)
