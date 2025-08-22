from rath.rath import Rath, current_rath
from typing import AsyncIterator, Iterator, Protocol, Type, TypeVar, Any, Dict, Optional
from pydantic import BaseModel

from rath.scalars import IDCoercible


# --- Base meta description ---
class TurmsMeta(Protocol):
    """Meta class for Turms operations"""

    document: str
    name: str
    type: str


TMeta = TypeVar("TMeta", bound=TurmsMeta)


class TurmsFragment(Protocol[TMeta]):
    """Represents a Turms operation that is both callable and its own return type."""

    Meta: Type[TMeta]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """A pydantic constructor"""
        ...


TFragment = TypeVar("TFragment", bound=TurmsFragment[Any])


def fetch_fragment_via(
    fragment: Type[TFragment],
    id: IDCoercible,
    rath: Optional[Rath] = None,
) -> TFragment:
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
    assert rath is not None, (
        "No rath client provided and no rath client in current_rath context"
    )
    return fragment(
        **rath.query(
            """
            %s
            query Entities($representations: [_Any!]!) {
                entities: _entities(representations: $representations) {
                    ...%s
                }
            }
            """
            % (
                fragment.Meta.document,
                fragment.Meta.name,
            ),
            {"representations": [{"__typename": fragment.Meta.type, "id": id}]},
        ).data["entities"][0],
    )


async def afetch_fragment_via(
    fragment: Type[TFragment],
    id: IDCoercible,
    rath: Optional[Rath] = None,
) -> TFragment:
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
    assert rath is not None, (
        "No rath client provided and no rath client in current_rath context"
    )
    return fragment(
        **(
            await rath.aquery(
                """
            %s
            query Entities($representations: [_Any!]!) {
                entities: _entities(representations: $representations) {
                    ...%s
                }
            }
            """
                % (
                    fragment.Meta.document,
                    fragment.Meta.name,
                ),
                {"representations": [{"__typename": fragment.Meta.name, "id": id}]},
            )
        ).data["entities"][0],
    )
