from rath import Rath
from rath.links import compose, DictingLink
from rath.links.testing.mock import AsyncMockLink, AsyncMockResolver
from rath.operation import Operation
import pytest


class QueryAsync(AsyncMockResolver):
    async def resolve_user(self, operation: Operation):
        return {"id": "1", "name": "John Doe", "email": "john.doe@gmail.com"}


class MutationAsync(AsyncMockResolver):
    pass

    async def change_user(self, operation: Operation):
        return {
            "id": operation.variables["id"],
            "name": "John Doe",
            "email": "john.doe@gmail.com",
        }


@pytest.fixture
def test_client():

    link = compose(
        ShrinkingLink(),
        DictingLink(),  # after the shrinking so we can override the dicting
        AsyncMockLink(
            query_resolver=QueryAsync(),
            mutation_resolver=MutationAsync(),
        ),
    )

    return Rath(link)
