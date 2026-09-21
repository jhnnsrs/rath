"""Objects that remember the client they were fetched with."""

from typing import TYPE_CHECKING, Any, Dict, Optional
from pydantic import BaseModel

if TYPE_CHECKING:
    from rath.rath import Rath


ORIGIN_KEY = "__rath_origin__"
"""Where an object keeps its origin, and the validation-context key it arrives under."""


class Origin:
    """Where an object came from: the client that fetched it, and what came with it.

    An object returned by a query carries no reference to the client that
    produced it, so anything it does later (fetch its data, re-fetch itself)
    would have to be handed a client again. An origin lets the object answer
    that itself, with the exact client that fetched it.

    ``client`` is the package's client (a ``Mikro``, say); ``rath`` its GraphQL
    client; ``clients`` any further clients it bound (a datalayer), by a name of
    the package's choosing.

    It lives in the instance ``__dict__`` under a non-field key rather than in a
    pydantic private attribute, because private attributes take part in ``==``:
    two identical objects would compare unequal merely for coming from different
    clients. Kept out of the way like this, equality, hashing, ``repr`` and dumps
    are unaffected, and ``model_copy`` carries it along.
    """

    __slots__ = ("client", "rath", "clients")

    def __init__(
        self, client: Any = None, rath: Optional["Rath"] = None, **clients: Any  # noqa: ANN401
    ) -> None:
        self.client = client
        self.rath = rath
        self.clients: Dict[str, Any] = clients

    def __deepcopy__(self, memo: Dict[int, Any]) -> "Origin":
        # A deep copy of the object still came from the same client, and the
        # client (its connections) must not be copied along with it.
        return self

    def __reduce__(self) -> Any:
        # The client does not travel with a pickled object: it arrives unbound.
        return (Origin, ())


def origin_context(
    client: Any = None, rath: Optional["Rath"] = None, **clients: Any  # noqa: ANN401
) -> Dict[str, Any]:
    """The validation context that binds every object built under it to an origin.

    Pass it as ``Model.model_validate(data, context=origin_context(...))``. Pydantic
    hands the validation context to the ``model_post_init`` of nested models too,
    so one call binds the whole result, however deep.
    """
    return {ORIGIN_KEY: Origin(client=client, rath=rath, **clients)}


def get_origin(obj: Any) -> Optional[Origin]:  # noqa: ANN401
    """The origin of an object, or ``None`` if it was not built under one."""
    return getattr(obj, "__dict__", {}).get(ORIGIN_KEY)


class ContextBound(BaseModel):
    """A model that remembers the client it was fetched with."""

    def model_post_init(self, context: Any) -> None:  # noqa: ANN401
        """Pick the origin up from the validation context, if there is one."""
        super().model_post_init(context)
        if isinstance(context, dict) and ORIGIN_KEY in context:
            # object.__setattr__: the generated models are frozen, and this is
            # deliberately neither a field nor a pydantic private attribute.
            object.__setattr__(self, ORIGIN_KEY, context[ORIGIN_KEY])

    def bound_client(self) -> Any:  # noqa: ANN401
        """The client this object was fetched with, or ``None``."""
        origin = get_origin(self)
        return origin.client if origin is not None else None

    def bound_rath(self) -> Optional["Rath"]:
        """The rath this object was fetched with, or ``None``."""
        origin = get_origin(self)
        return origin.rath if origin is not None else None


__all__ = ["ORIGIN_KEY", "Origin", "origin_context", "get_origin", "ContextBound"]
