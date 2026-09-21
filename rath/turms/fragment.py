from rath.origin import origin_context
from rath.rath import Rath
from typing import Any, Dict, List, Optional, Protocol, Sequence, Type, TypeVar

from rath.errors import EntityNotFound

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


ENTITIES_QUERY = """
%s
query Entities($representations: [_Any!]!) {
    entities: _entities(representations: $representations) {
        ...%s
    }
}
"""


def _entities_request(
    fragment: Type[TFragment], ids: Sequence[IDCoercible]
) -> tuple[str, Dict[str, Any]]:
    """The ``_entities`` document and variables that fetch ``ids`` as ``fragment``.

    The fragment is spread by its *name*, but the representation names the *type*
    the fragment is on. The two differ for every fragment that is not named after
    its type (``fragment ListImage on Image``), and the server resolves the
    reference by the typename.
    """
    document = ENTITIES_QUERY % (fragment.Meta.document, fragment.Meta.name)
    representations = [{"__typename": fragment.Meta.type, "id": id} for id in ids]
    return document, {"representations": representations}


def _build(
    fragment: Type[TFragment],
    entities: Sequence[Any],
    ids: Sequence[IDCoercible],
    context: Dict[str, Any],
) -> List[Optional[TFragment]]:
    if len(entities) != len(ids):
        raise EntityNotFound(
            f"Asked for {len(ids)} {fragment.Meta.type} entities and got "
            f"{len(entities)} back. `_entities` answers one per representation."
        )
    return [
        None if entity is None else fragment.model_validate(entity, context=context)  # type: ignore[attr-defined]
        for entity in entities
    ]


def fetch_fragments_via(
    fragment: Type[TFragment],
    ids: Sequence[IDCoercible],
    rath: Rath,
    origin: Optional[Dict[str, Any]] = None,
) -> List[Optional[TFragment]]:
    """Fetch several entities of one type in a single ``_entities`` request.

    The result is in the order of ``ids``, with ``None`` where the server has no
    such entity (or none the caller may see: the two are deliberately the same).

    Parameters
    ----------
    fragment : Type[TFragment]
        The turms fragment to fetch the entities as
    ids : Sequence[IDCoercible]
        The ids to fetch. No request is made for an empty sequence.
    rath : Rath
        The rath client to fetch through.
    origin : Dict[str, Any], optional
        The validation context to build the objects under, as returned by
        ``rath.origin.origin_context``. A package that binds further clients to
        what it fetches (a datalayer, say) passes its own here. By default the
        objects are bound to ``rath`` alone.
    """
    if not ids:
        return []
    document, variables = _entities_request(fragment, ids)
    entities = rath.query(document, variables).data["entities"]
    return _build(fragment, entities, ids, origin or origin_context(rath=rath))


async def afetch_fragments_via(
    fragment: Type[TFragment],
    ids: Sequence[IDCoercible],
    rath: Rath,
    origin: Optional[Dict[str, Any]] = None,
) -> List[Optional[TFragment]]:
    """Fetch several entities of one type in a single ``_entities`` request.

    The async twin of :func:`fetch_fragments_via`; see there for the parameters.
    """
    if not ids:
        return []
    document, variables = _entities_request(fragment, ids)
    entities = (await rath.aquery(document, variables)).data["entities"]
    return _build(fragment, entities, ids, origin or origin_context(rath=rath))


def _only(fragment: Type[TFragment], id: IDCoercible, found: List[Optional[TFragment]]) -> TFragment:
    entity = found[0]
    if entity is None:
        raise EntityNotFound(f"No {fragment.Meta.type} with id {id!r} (or none you may see).")
    return entity


def fetch_fragment_via(
    fragment: Type[TFragment],
    id: IDCoercible,
    rath: Rath,
    origin: Optional[Dict[str, Any]] = None,
) -> TFragment:
    """Fetch one entity by id through ``_entities``.

    See :func:`fetch_fragments_via` for the parameters.

    Raises
    ------
    EntityNotFound
        If the server has no such entity.
    """
    return _only(fragment, id, fetch_fragments_via(fragment, [id], rath, origin))


async def afetch_fragment_via(
    fragment: Type[TFragment],
    id: IDCoercible,
    rath: Rath,
    origin: Optional[Dict[str, Any]] = None,
) -> TFragment:
    """Fetch one entity by id through ``_entities``.

    The async twin of :func:`fetch_fragment_via`.
    """
    return _only(fragment, id, await afetch_fragments_via(fragment, [id], rath, origin))
