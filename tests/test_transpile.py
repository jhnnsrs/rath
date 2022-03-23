from rath.links.testing.mock import AsyncMockLink, AsyncMockResolver
from rath.links.transpile import TranspileLink, TranspileRegistry
from rath.links import compose
from rath import Rath
from rath.operation import Operation
from tests.apis.nested_inputs import (
    BeastVector,
    acreate_transpiled_beast,
    create_transpiled_beast,
)


class MutationAsyncTranspiled(AsyncMockResolver):
    async def resolve_createTranspiledBeast(self, operation: Operation):
        assert isinstance(operation.variables, dict), "Not a dict"
        assert isinstance(
            operation.variables["vectors"][0], BeastVector
        ), "SHould have been tranpiled to a BeastVector"
        return {"id": "1", "legs": 1}


async def test_transpile_async():
    """Tests transpilation"""

    registry = TranspileRegistry()

    @registry.register_list(
        "BeastVector", lambda x, depth: isinstance(x, list) and depth == 1
    )
    def transpile_beasts(value, depth):
        return [BeastVector(x=i[0], y=i[1]) for i in value]

    rath = Rath(
        link=compose(
            TranspileLink(registry=registry),
            AsyncMockLink(
                mutation_resolver=MutationAsyncTranspiled().to_dict(),
            ),
        )
    )

    async with rath:

        x = await acreate_transpiled_beast(non_optional_parameter=1, vectors=[[2, 3]])


async def test_transpile_sync():
    """Tests transpilation"""

    registry = TranspileRegistry()

    @registry.register_list(
        "BeastVector", lambda x, depth: isinstance(x, list) and depth == 1
    )
    def transpile_beasts(value, depth):
        return [BeastVector(x=i[0], y=i[1]) for i in value]

    rath = Rath(
        link=compose(
            TranspileLink(registry=registry),
            AsyncMockLink(
                mutation_resolver=MutationAsyncTranspiled().to_dict(),
            ),
        )
    )
    with rath:

        x = create_transpiled_beast(non_optional_parameter=1, vectors=[[2, 3]])
