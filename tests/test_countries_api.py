from rath.links.validate import ValidatingLink, ValidationError
from rath.operation import Operation, opify
import pytest
from rath.links import compose
from rath.links.testing.mock import AsyncMockLink, AsyncMockResolver
from tests.apis.countries import acountries, countries
from rath import Rath
from tests.mocks import QueryAsync, MutationAsync, SubscriptionAsync
from rath.links.aiohttp import AIOHttpLink


@pytest.fixture()
def real_world_link():
    return AIOHttpLink(url="https://countries.trevorblades.com/")


async def test_query_async(real_world_link):

    rath = Rath(link=real_world_link)

    async with rath:
        countries = await acountries()

    assert isinstance(countries, list), "Not a list"


def test_query_sync(real_world_link):

    rath = Rath(link=real_world_link)

    with rath:
        xcountries = countries()

    assert isinstance(xcountries, list), "Not a list"


async def test_validation(real_world_link):

    link = ValidatingLink()

    rath = Rath(link=compose(link, real_world_link))
    r = await rath.aconnect()

    with pytest.raises(ValidationError):
        await rath.aexecute(
            """
            query {
                beast(leg: 1) {
                    binomial
                }
            }
            """
        )

    await rath.aexecute(
        """
            query {
                countries {
                    phone
                }
            }
            """
    )

    await r.adisconnect()
