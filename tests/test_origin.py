"""Objects remember the client they were fetched with."""

import copy
import pickle
from types import SimpleNamespace
from typing import Any, List, Optional

import pytest
from pydantic import BaseModel, ConfigDict

from rath.origin import ORIGIN_KEY, ContextBound, Origin, get_origin, origin_context
from rath.traits import FederationFetchable
from rath.errors import EntityNotFound
from rath.turms.fragment import (
    afetch_fragment_via,
    afetch_fragments_via,
    fetch_fragment_via,
    fetch_fragments_via,
)


class Store(ContextBound, BaseModel):
    model_config = ConfigDict(frozen=True)
    id: str


class Dataset(ContextBound, BaseModel):
    model_config = ConfigDict(frozen=True)
    id: str
    store: Store
    views: List[Store]
    maybe: Optional[Store] = None


class Operation(BaseModel):
    """Like a generated operation: not bound itself, it only wraps the result."""

    model_config = ConfigDict(frozen=True)
    dataset: Dataset


class UncopyableApp:
    """Stands in for an app: it owns clients and connections, and must stay where it is."""

    def __deepcopy__(self, memo: dict[int, Any]) -> Any:
        raise AssertionError("the app was deep-copied along with an object")

    def __reduce__(self) -> Any:
        raise AssertionError("the app was pickled along with an object")


DATA = {
    "id": "1",
    "store": {"id": "s"},
    "views": [{"id": "v"}],
    "maybe": {"id": "m"},
}


@pytest.fixture()
def app() -> UncopyableApp:
    return UncopyableApp()


@pytest.fixture()
def bound(app: UncopyableApp) -> Dataset:
    return Dataset.model_validate(DATA, context=origin_context(client=app, rath="client"))


def test_one_validation_binds_the_whole_result(app: UncopyableApp) -> None:
    operation = Operation.model_validate(
        {"dataset": DATA}, context=origin_context(client=app)
    )
    dataset = operation.dataset

    for obj in (dataset, dataset.store, dataset.views[0], dataset.maybe):
        assert obj is not None and obj.bound_client() is app


def test_an_object_built_without_a_context_is_unbound() -> None:
    plain = Dataset(**DATA)

    assert get_origin(plain) is None
    assert plain.bound_client() is None
    assert plain.bound_rath() is None


def test_binding_carries_the_client_too(bound: Dataset) -> None:
    assert bound.bound_rath() == "client"
    assert bound.store.bound_rath() == "client"


def test_binding_does_not_take_part_in_equality_or_hashing(bound: Dataset) -> None:
    """A pydantic private attribute would: identical objects from two apps compared unequal."""
    plain = Dataset(**DATA)

    assert bound == plain and plain == bound
    assert hash(bound.store) == hash(plain.store)
    assert len({bound.store, plain.store}) == 1


def test_binding_is_invisible_in_dumps_and_repr(bound: Dataset) -> None:
    plain = Dataset(**DATA)

    assert bound.model_dump() == plain.model_dump()
    assert ORIGIN_KEY not in bound.model_dump_json()
    assert ORIGIN_KEY not in repr(bound)
    assert bound.model_fields_set == plain.model_fields_set
    assert bound.model_extra is None


def test_model_copy_keeps_the_binding(bound: Dataset, app: UncopyableApp) -> None:
    assert bound.model_copy().bound_client() is app
    assert bound.model_copy(update={"id": "2"}).bound_client() is app


def test_deepcopy_keeps_the_binding_without_copying_the_app(
    bound: Dataset, app: UncopyableApp
) -> None:
    copied = copy.deepcopy(bound)

    assert copied.bound_client() is app
    assert copied.store.bound_client() is app


def test_pickling_drops_the_binding_instead_of_the_app(bound: Dataset) -> None:
    restored = pickle.loads(pickle.dumps(bound))

    assert restored == bound
    assert restored.bound_client() is None


def test_origin_survives_being_shared() -> None:
    origin = Origin(ctx="app")

    assert copy.deepcopy(origin) is origin


# --------------------------------------------------------------------------- #
# Re-fetching an entity
# --------------------------------------------------------------------------- #


class Entity(ContextBound, FederationFetchable, BaseModel):
    model_config = ConfigDict(frozen=True)
    id: str

    class Meta:
        document = "fragment Entity on Entity { id }"
        name = "Entity"
        type = "Entity"



class FakeRath:
    def __init__(self) -> None:
        self.queries: list[dict[str, Any]] = []

    def _result(self, variables: dict[str, Any]) -> Any:
        self.queries.append(variables)
        return SimpleNamespace(data={"entities": [{"id": "7"}]})

    def query(self, query: str, variables: dict[str, Any]) -> Any:
        return self._result(variables)

    async def aquery(self, query: str, variables: dict[str, Any]) -> Any:
        return self._result(variables)


def test_fetched_entity_is_bound_to_what_fetched_it() -> None:
    rath = FakeRath()

    entity = fetch_fragment_via(
        Entity, id="7", rath=rath, origin=origin_context(client="app", rath=rath)  # type: ignore[arg-type]
    )

    assert entity.id == "7"
    assert entity.bound_client() == "app"
    assert entity.bound_rath() is rath


@pytest.mark.asyncio
async def test_async_fetched_entity_is_bound_too() -> None:
    rath = FakeRath()

    entity = await afetch_fragment_via(
        Entity, id="7", rath=rath, origin=origin_context(client="app", rath=rath)  # type: ignore[arg-type]
    )

    assert entity.bound_client() == "app"
    assert entity.bound_rath() is rath


def test_expand_fetches_through_the_client_it_is_handed() -> None:
    mine, other = SimpleNamespace(rath=FakeRath()), SimpleNamespace(rath=FakeRath())

    entity = Entity.expand("7", mine)

    assert entity.bound_client() is mine
    assert len(mine.rath.queries) == 1 and other.rath.queries == []


def test_origin_carries_further_clients_by_name(app: UncopyableApp) -> None:
    """A package binds whatever else it resolved at fetch time, under its own names."""
    bound = Dataset.model_validate(
        DATA, context=origin_context(rath="client", datalayer="layer")
    )
    origin = get_origin(bound.store)

    assert origin is not None
    assert origin.clients == {"datalayer": "layer"}
    assert origin.client is None and origin.rath == "client"


# --------------------------------------------------------------------------- #
# The `_entities` request itself
# --------------------------------------------------------------------------- #


class InstanceRef(ContextBound, FederationFetchable, BaseModel):
    """A fragment that is not named after the type it is on."""

    id: str

    class Meta:
        document = "fragment InstanceRef on Instance { id }"
        name = "InstanceRef"
        type = "Instance"

    @classmethod
    def get_rath(cls, ctx: Any = None) -> Any:
        return ctx.rath


class RecordingRath:
    """Answers `_entities` from a table, and remembers what it was asked."""

    def __init__(self, known: dict[str, dict[str, Any]]) -> None:
        self.known = known
        self.requests: list[tuple[str, dict[str, Any]]] = []

    def _result(self, query: str, variables: dict[str, Any]) -> Any:
        self.requests.append((query, variables))
        entities = [self.known.get(rep["id"]) for rep in variables["representations"]]
        return SimpleNamespace(data={"entities": entities})

    def query(self, query: str, variables: dict[str, Any]) -> Any:
        return self._result(query, variables)

    async def aquery(self, query: str, variables: dict[str, Any]) -> Any:
        return self._result(query, variables)


def _sent(rath: RecordingRath) -> tuple[str, list[dict[str, Any]]]:
    query, variables = rath.requests[-1]
    return query, variables["representations"]


def test_the_representation_names_the_type_and_the_spread_names_the_fragment() -> None:
    rath = RecordingRath({"7": {"id": "7"}})

    fetch_fragment_via(InstanceRef, id="7", rath=rath)  # type: ignore[arg-type]

    query, representations = _sent(rath)
    assert representations == [{"__typename": "Instance", "id": "7"}]
    assert "...InstanceRef" in query


@pytest.mark.asyncio
async def test_the_async_representation_names_the_type_too() -> None:
    """It sent the fragment's name, which only works while the two are equal."""
    rath = RecordingRath({"7": {"id": "7"}})

    await afetch_fragment_via(InstanceRef, id="7", rath=rath)  # type: ignore[arg-type]

    query, representations = _sent(rath)
    assert representations == [{"__typename": "Instance", "id": "7"}]
    assert "...InstanceRef" in query


@pytest.mark.asyncio
async def test_many_ids_are_one_request_answered_in_order() -> None:
    rath = RecordingRath({"1": {"id": "1"}, "3": {"id": "3"}})

    found = await afetch_fragments_via(
        InstanceRef, ["3", "2", "1"], rath=rath, origin=origin_context(client="app")  # type: ignore[arg-type]
    )

    assert len(rath.requests) == 1
    assert [entity and entity.id for entity in found] == ["3", None, "1"]
    assert found[0] is not None and found[0].bound_client() == "app"


def test_the_sync_batch_matches_the_async_one() -> None:
    rath = RecordingRath({"1": {"id": "1"}})

    found = fetch_fragments_via(InstanceRef, ["1", "9"], rath=rath)  # type: ignore[arg-type]

    assert len(rath.requests) == 1
    assert [entity and entity.id for entity in found] == ["1", None]


def test_no_ids_is_no_request() -> None:
    rath = RecordingRath({})

    assert fetch_fragments_via(InstanceRef, [], rath=rath) == []  # type: ignore[arg-type]
    assert rath.requests == []


def test_a_missing_entity_is_a_lookup_error_not_a_validation_error() -> None:
    rath = RecordingRath({})

    with pytest.raises(EntityNotFound, match="No Instance with id '9'"):
        fetch_fragment_via(InstanceRef, id="9", rath=rath)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_a_missing_entity_is_a_lookup_error_async() -> None:
    with pytest.raises(LookupError):
        await afetch_fragment_via(InstanceRef, id="9", rath=RecordingRath({}))  # type: ignore[arg-type]


def test_the_caller_can_supply_the_origin() -> None:
    """So a package binds its other clients to what federation fetched."""
    rath = RecordingRath({"7": {"id": "7"}})

    entity = fetch_fragment_via(
        InstanceRef,
        id="7",
        rath=rath,  # type: ignore[arg-type]
        origin=origin_context(client="app", rath=rath, datalayer="layer"),  # type: ignore[arg-type]
    )

    origin = get_origin(entity)
    assert origin is not None and origin.clients == {"datalayer": "layer"}


class LayeredRef(InstanceRef):
    @classmethod
    def fetch_origin(cls, client: Any) -> Any:
        return origin_context(client=client, rath=client.rath, datalayer=client.datalayer)


@pytest.mark.asyncio
async def test_a_type_binds_its_own_clients_to_what_it_expands() -> None:
    app = SimpleNamespace(rath=RecordingRath({"1": {"id": "1"}}), datalayer="layer")

    one = await LayeredRef.aexpand("1", app)
    many = await LayeredRef.aexpand_many(["1", "2"], app)

    assert get_origin(one).clients == {"datalayer": "layer"}  # type: ignore[union-attr]
    assert many[1] is None and get_origin(many[0]).clients == {"datalayer": "layer"}  # type: ignore[union-attr]


# --------------------------------------------------------------------------- #
# federated(): the pair of expanders a structure description takes
# --------------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_federated_expanders_fetch_through_the_client_they_are_handed() -> None:
    from rath.turms.federation import federated

    mine = SimpleNamespace(rath=RecordingRath({"1": {"id": "1"}, "2": {"id": "2"}}))
    other = SimpleNamespace(rath=RecordingRath({}))
    expanders = federated(InstanceRef)

    one = await expanders["aexpand"](mine, "1")
    many = await expanders["aexpand_many"](mine, ["2", "9", "1"])

    assert one.id == "1" and one.bound_client() is mine
    assert [entity and entity.id for entity in many] == ["2", None, "1"]
    assert len(mine.rath.requests) == 2 and other.rath.requests == []


@pytest.mark.asyncio
async def test_federated_expanders_bind_what_the_package_binds() -> None:
    from rath.turms.federation import federated

    client = SimpleNamespace(rath=RecordingRath({"1": {"id": "1"}}))
    expanders = federated(
        InstanceRef,
        origin=lambda c: origin_context(client=c, rath=c.rath, datalayer="layer"),
    )

    (entity,) = await expanders["aexpand_many"](client, ["1"])

    assert get_origin(entity).clients == {"datalayer": "layer"}  # type: ignore[union-attr]
