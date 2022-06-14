from urllib.robotparser import RequestRate
from urllib.robotparser import RequestRate
import requests
from testcontainers.compose import DockerCompose
import pytest
from rath import Rath
from rath.links.aiohttp import AIOHttpLink
from .integration.utils import wait_for_http_response
from .utils import build_relative


@pytest.mark.integration
@pytest.fixture()
def integration_link():
    return AIOHttpLink(endpoint_url="http://localhost:5454/graphql")


@pytest.mark.integration
@pytest.fixture(scope="session")
def environment():
    with DockerCompose(
        filepath=build_relative("integration"),
        compose_file_name="docker-compose.yaml",
    ) as compose:
        wait_for_http_response("http://localhost:5454/ht", max_retries=5)
        yield


@pytest.mark.integration
def test_connection_x(environment, integration_link):

    rath = Rath(link=integration_link)
    with rath:

        answer = rath.query(
            """query {
                    miniModels {
                        id
                    }
            }"""
        )

        assert answer, "No answer received"
