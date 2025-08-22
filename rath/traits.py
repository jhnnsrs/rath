from typing import Any, TypeVar, Type
from rath import Rath
from rath.scalars import IDCoercible
from rath.turms.fragment import fetch_fragment_via, TurmsFragment, afetch_fragment_via
from rath.turms.utils import get_attributes_or_error

T = TypeVar("T", bound=TurmsFragment[Any])


class FederationFetchable:
    @classmethod
    def get_identifier(cls: Type[T]) -> str:
        """Get the identifier for the fragment."""
        return cls.Meta.type

    @classmethod
    def get_rath(cls: Type[T]) -> "Rath":
        """Get the current Rath client from the context."""
        raise NotImplementedError(
            "This method should be implemented by the subclass to return the current Rath client."
        )

    @classmethod
    def expand(cls: Type[T], id: IDCoercible) -> T:
        """Fetch an entity by its ID using the current Rath client."""
        return fetch_fragment_via(
            cls,
            id=id,
            rath=cls.get_rath(),
        )

    @classmethod
    async def aexpand(cls: Type[T], id: IDCoercible) -> T:
        """Asynchronously fetch an entity by its ID using the current Rath client."""
        return await afetch_fragment_via(
            cls,
            id=id,
            rath=cls.get_rath(),
        )

    async def ashrink(self) -> None:
        """Asynchronously shrink the entity."""
        return get_attributes_or_error(self, "id")

    def shrink(self) -> None:
        """Shrink the entity."""
        return get_attributes_or_error(self, "id")
