"""Expanding and shrinking a client's structures by identifier.

A structure travels between apps as an identifier (``@mikro/arraydataset``) and an
id. The client that owns it turns the id back into the object and the object into
its id. :class:`ExpandsStructures` is that behaviour for a generated client: it
names one expander per identifier, and gets batch expansion and shrinking for free.

rekuest delegates to exactly these three methods (its ``StructureClient``
protocol), so a client that mixes this in serves as its service's structure
client without importing rekuest::

    class Mikro(Composition, MikroApi, ExpandsStructures):
        EXPANDERS = {
            "@mikro/arraydataset": MikroApi.aget_array_dataset,
            "@mikro/file": MikroApi.aget_file,
        }
"""

import asyncio
from collections.abc import Awaitable, Callable, Mapping, Sequence
from typing import Any, ClassVar

from rath.scalars import ID


class UnknownStructureError(LookupError):
    """A client was asked to expand an identifier it names no expander for."""


class ExpandsStructures:
    """Expand and shrink structures by identifier, through this client.

    A client names one expander per identifier in :attr:`EXPANDERS` -- usually an
    unbound method of its generated API, called as ``expander(client, id)``.
    :meth:`aexpand_many` and :meth:`ashrink` have defaults a client overrides where
    it can do better (one batched request; an id that is not ``obj.id``).
    """

    EXPANDERS: ClassVar[Mapping[str, Callable[[Any, ID], Awaitable[Any]]]] = {}
    """The expander for each identifier, called as ``expander(client, id)``."""

    async def aexpand(self, identifier: str, id: ID) -> Any:  # noqa: ANN401
        """Expand ``id`` with the expander named for ``identifier``.

        Args:
            identifier: The structure's identifier, e.g. ``@mikro/arraydataset``.
            id: The id to expand.

        Returns:
            The object.

        Raises:
            UnknownStructureError: If this client names no expander for
                ``identifier``.
        """
        expander = self.EXPANDERS.get(identifier)
        if expander is None:
            known = ", ".join(sorted(self.EXPANDERS)) or "none"
            raise UnknownStructureError(
                f"{type(self).__name__} cannot expand '{identifier}': it names no "
                f"expander for it in EXPANDERS (it has: {known})."
            )
        return await expander(self, id)

    async def aexpand_many(self, identifier: str, ids: Sequence[ID]) -> Sequence[Any]:
        """Expand several ids, one :meth:`aexpand` each, concurrently.

        Args:
            identifier: The structure's identifier.
            ids: The ids to expand.

        Returns:
            One object per id, in order.

        Raises:
            UnknownStructureError: If this client names no expander for
                ``identifier``.
        """
        return list(await asyncio.gather(*(self.aexpand(identifier, id) for id in ids)))

    async def ashrink(self, identifier: str, obj: Any) -> ID:  # noqa: ANN401
        """Shrink ``obj`` to its ``id`` attribute.

        Args:
            identifier: The structure's identifier.
            obj: The object to shrink.

        Returns:
            ``obj.id``.
        """
        shrunk: ID = obj.id
        return shrunk


__all__ = ["ExpandsStructures", "UnknownStructureError"]
