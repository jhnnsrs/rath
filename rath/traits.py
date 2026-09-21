from typing import Any, Dict, List, Optional, Sequence, TypeVar, Type
from rath.origin import (
    ORIGIN_KEY as ORIGIN_KEY,
    ContextBound as ContextBound,
    Origin as Origin,
    get_origin as get_origin,
    origin_context as origin_context,
)
from rath.scalars import IDCoercible
from rath.turms.fragment import (
    TurmsFragment,
    afetch_fragment_via,
    afetch_fragments_via,
    fetch_fragment_via,
    fetch_fragments_via,
)
from rath.turms.utils import get_attributes_or_error

T = TypeVar("T", bound=TurmsFragment[Any])


class FederationFetchable:
    """A generated type that can be fetched by id through ``_entities``.

    Every fetch goes through the client it is handed -- the package's client (a
    ``Mikro``, say), which has a ``rath``. Nothing is looked up.
    """

    @classmethod
    def get_identifier(cls: Type[T]) -> str:
        """Get the identifier for the fragment."""
        return cls.Meta.type

    @classmethod
    def fetch_origin(cls: Type[T], client: Any) -> Dict[str, Any]:  # noqa: ANN401
        """The validation context fetched entities are built under.

        A package whose objects need more than the rath later on (a datalayer,
        say) overrides this to bind it, so an entity fetched here is as capable as
        one returned by the package's own operations.
        """
        return origin_context(client=client, rath=client.rath)

    @classmethod
    def expand(cls: Type[T], id: IDCoercible, client: Any) -> T:  # noqa: ANN401
        """Fetch an entity by its ID through ``client``."""
        return fetch_fragment_via(
            cls, id=id, rath=client.rath, origin=cls.fetch_origin(client)
        )

    @classmethod
    async def aexpand(cls: Type[T], id: IDCoercible, client: Any) -> T:  # noqa: ANN401
        """Asynchronously fetch an entity by its ID through ``client``."""
        return await afetch_fragment_via(
            cls, id=id, rath=client.rath, origin=cls.fetch_origin(client)
        )

    @classmethod
    def expand_many(
        cls: Type[T], ids: Sequence[IDCoercible], client: Any  # noqa: ANN401
    ) -> List[Optional[T]]:
        """Fetch several entities in one request, ``None`` where there is none."""
        return fetch_fragments_via(
            cls, ids=ids, rath=client.rath, origin=cls.fetch_origin(client)
        )

    @classmethod
    async def aexpand_many(
        cls: Type[T], ids: Sequence[IDCoercible], client: Any  # noqa: ANN401
    ) -> List[Optional[T]]:
        """Asynchronously fetch several entities in one request, in the order of ``ids``."""
        return await afetch_fragments_via(
            cls, ids=ids, rath=client.rath, origin=cls.fetch_origin(client)
        )

    async def ashrink(self) -> None:
        """Asynchronously shrink the entity."""
        return get_attributes_or_error(self, "id")

    def shrink(self) -> None:
        """Shrink the entity."""
        return get_attributes_or_error(self, "id")
