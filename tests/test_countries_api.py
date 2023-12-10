from rath.links.validate import ValidatingLink, ValidationError
import pytest
from rath.links import compose
from .apis.countries import acountries, countries
from rath import Rath
from rath.links.aiohttp import AIOHttpLink


@pytest.mark.public
@pytest.fixture()
def real_world_link():
    return AIOHttpLink(endpoint_url="https://countries.trevorblades.com/")


@pytest.mark.public
async def test_query_async(real_world_link):
    rath = Rath(link=real_world_link)

    async with rath:
        countries = await acountries()

    assert isinstance(countries, list), "Not a list"


@pytest.mark.public
def test_query_sync(real_world_link):
    rath = Rath(link=real_world_link)

    with rath:
        xcountries = countries()

    assert isinstance(xcountries, list), "Not a list"


@pytest.mark.public
async def test_validation(real_world_link):
    link = ValidatingLink(allow_introspection=True)

    rath = Rath(link=compose(link, real_world_link))
    async with rath as r:
        with pytest.raises(ValidationError):
            await rath.aquery(
                """
                query {
                    beast(leg: 1) {
                        binomial
                    }
                }
                """
            )

        await rath.aquery(
            """
                query {
                    countries {
                        phone
                    }
                }
                """
        )
