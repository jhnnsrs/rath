from pydantic import BaseModel
from rath.links.compose import compose
from rath.links.dictinglink import DictingLink
from rath.links.testing.mock import AsyncMockLink, AsyncMockResolver
from rath.rath import Rath
from tests.mocks import QueryAsync, MutationAsync
import pytest


class MutationAsync(AsyncMockResolver):
    async def resolve_createBeast(self, operation):
        assert operation.variables["dict"]["a"] == 1
        return {"id": "1", "legs": 1}


@pytest.fixture()
def mock_link():
    return AsyncMockLink(query_resolver=QueryAsync(), mutation_resolver=MutationAsync())


async def test_validation(mock_link):

    link = DictingLink()

    class DictableX(BaseModel):
        a: int

    rath = Rath(compose(link, mock_link))
    async with rath:
        await rath.aexecute(
            """
            mutation beaste($name: String!, $email: String!) {
                createBeast(id: "1") {
                    binomial
                }
            }
            """,
            variables={"name": "John Doe", "dict": DictableX(a=1)},
        )
