import pytest
from rath.links.testing.mock import AsyncMockLink
from .apis.tests import get_beasts, aget_beasts
from rath import Rath
from .mocks import MutationAsync, QueryAsync


@pytest.fixture()
def mock_link():
    return AsyncMockLink(
        query_resolver=QueryAsync().to_dict(),
        mutation_resolver=MutationAsync().to_dict(),
    )


async def test_query_async(mock_link):

    rath = Rath(link=mock_link)

    async with rath:
        beasts = await aget_beasts()

        assert isinstance(beasts, list), "Not a list"


def test_query_sync(mock_link):

    rath = Rath(link=mock_link)

    with rath:
        beasts = get_beasts()

        assert isinstance(beasts, list), "Not a list"
        for be in beasts:
            assert be.common_name is not None, "Common Name should be resolved"
