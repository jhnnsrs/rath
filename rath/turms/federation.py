"""Expanding structures through federation.

Every service whose types carry ``@key(fields: "id")`` answers
``_entities(representations:)``, which is the one way to fetch by id that takes a
*list*. :func:`federated` turns a generated fragment into the pair of expanders a
structure description takes, so a list port of N such structures is one request.
The client is the one the structure registry was bound to.

A type is only reachable this way if it is in the service's ``_Entity`` union, and
the lookup is only as well scoped as the server makes it: check that the service
scopes ``_entities`` like its ``get_x`` queries before switching a type over.
"""

from collections.abc import Callable, Sequence
from typing import Any

from rath.origin import HasRath
from rath.scalars import IDCoercible
from rath.turms.fragment import TFragment, afetch_fragment_via, afetch_fragments_via

OriginBuilder = Callable[[Any], dict[str, Any]]
"""``origin(client)``: the validation context fetched objects are bound under."""


def federated(
    fragment: type[TFragment],
    origin: OriginBuilder | None = None,
) -> dict[str, Any]:
    """The ``aexpand`` and ``aexpand_many`` that fetch ``fragment`` through ``_entities``.

    Both take the client first (``aexpand(client, id)``), so a client can use them
    as its expanders for ``fragment``'s identifier (see :mod:`rath.expansion`)::

        pair = federated(Flow)

        class Fluss(Composition, FlussApi, ExpandsStructures):
            EXPANDERS = {"@fluss/flow": pair["aexpand"]}

            async def aexpand_many(self, identifier, ids):
                return await pair["aexpand_many"](self, ids)

    Parameters
    ----------
    fragment : Type[TFragment]
        The generated fragment to fetch. It names both the selection and the type.
    origin : OriginBuilder, optional
        ``origin(client)`` builds what the fetched objects are bound to. A package
        passes the one its operations use, so that what federation fetched is as
        capable as what a query returned. By default: the client and its rath.
    """
    from rath.origin import origin_context

    def bound_to(client: HasRath) -> dict[str, Any]:
        if origin is not None:
            return origin(client)
        return origin_context(client=client, rath=client.rath)

    async def aexpand(client: HasRath, id: IDCoercible) -> TFragment:
        return await afetch_fragment_via(
            fragment, id, rath=client.rath, origin=bound_to(client)
        )

    async def aexpand_many(
        client: HasRath,
        ids: Sequence[IDCoercible],
    ) -> list[TFragment | None]:
        return await afetch_fragments_via(
            fragment, ids, rath=client.rath, origin=bound_to(client)
        )

    return {"aexpand": aexpand, "aexpand_many": aexpand_many}


__all__ = ["federated"]
