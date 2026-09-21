"""ExpandsStructures: a client expands and shrinks its structures by identifier."""

from typing import Any, Sequence

import pytest

from rath.expansion import ExpandsStructures, UnknownStructureError


class Thing:
    def __init__(self, id: str, owner: str) -> None:
        self.id = id
        self.owner = owner


class ThingClient(ExpandsStructures):
    def __init__(self, owner: str) -> None:
        self.owner = owner

    async def aget_thing(self, id: str) -> Thing:
        return Thing(id, self.owner)

    EXPANDERS = {"@things/thing": aget_thing}


class BatchingClient(ThingClient):
    def __init__(self, owner: str) -> None:
        super().__init__(owner)
        self.batches: list[list[str]] = []

    async def aexpand_many(self, identifier: str, ids: Sequence[str]) -> Sequence[Any]:
        self.batches.append(list(ids))
        return [Thing(id, self.owner) for id in ids]


class LabelClient(ThingClient):
    async def ashrink(self, identifier: str, obj: Any) -> str:  # noqa: ANN401
        return f"label:{obj.id}"


@pytest.mark.asyncio
async def test_expands_through_the_expander_named_for_the_identifier() -> None:
    thing = await ThingClient("A").aexpand("@things/thing", "1")
    assert (thing.id, thing.owner) == ("1", "A")


@pytest.mark.asyncio
async def test_an_unknown_identifier_names_the_client_and_what_it_knows() -> None:
    with pytest.raises(UnknownStructureError, match=r"ThingClient cannot expand '@x/y'.*@things/thing"):
        await ThingClient("A").aexpand("@x/y", "1")


@pytest.mark.asyncio
async def test_expanding_many_answers_in_order_by_default() -> None:
    things = await ThingClient("A").aexpand_many("@things/thing", ["3", "1", "2"])
    assert [t.id for t in things] == ["3", "1", "2"]


@pytest.mark.asyncio
async def test_a_client_can_batch_instead() -> None:
    client = BatchingClient("A")
    await client.aexpand_many("@things/thing", ["1", "2"])
    assert client.batches == [["1", "2"]]


@pytest.mark.asyncio
async def test_shrinking_is_the_id_unless_the_client_says_otherwise() -> None:
    assert await ThingClient("A").ashrink("@things/thing", Thing("7", "A")) == "7"
    assert await LabelClient("A").ashrink("@things/thing", Thing("7", "A")) == "label:7"
