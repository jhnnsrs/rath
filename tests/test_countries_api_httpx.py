import pytest

from rath import Rath
from rath.links import compose
from rath.links.httpx import HttpxLink
from rath.links.validate import ValidatingLink, ValidationError

from .apis.countries import acountries, countries


@pytest.mark.public
@pytest.fixture()
def real_world_link() -> HttpxLink:
    return HttpxLink(endpoint_url="https://countries.trevorblades.com/")


@pytest.mark.public
async def test_query_async(real_world_link: HttpxLink) -> None:
    rath = Rath(link=real_world_link)

    async with rath:
        countries = await acountries(rath)

    assert isinstance(countries, list), "Not a list"


@pytest.mark.public
def test_query_sync(real_world_link: HttpxLink) -> None:
    rath = Rath(link=real_world_link)

    with rath:
        xcountries = countries(rath)

    assert isinstance(xcountries, list), "Not a list"


@pytest.mark.public
async def test_validation(real_world_link: HttpxLink) -> None:
    link = ValidatingLink(allow_introspection=True)

    rath = Rath(link=compose(link, real_world_link))
    r = await rath.aenter()

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

    await r.aexit()
