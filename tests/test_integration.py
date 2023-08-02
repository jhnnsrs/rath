from testcontainers.compose import DockerCompose
import pytest
from rath import Rath
from rath.links.aiohttp import AIOHttpLink
from .integration.utils import wait_for_http_response
from .utils import build_relative
import subprocess


class DockerV2Compose(DockerCompose):
    @property
    def docker_cmd_comment(self):
        """Returns the base docker command by testing the docker compose api

        Returns:
            list[ſt]: _description_
        """
        return (
            ["docker", "compose"]
            if subprocess.run(
                ["docker", "compose", "--help"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            ).returncode
            == 0
            else ["docker-compose"]
        )

    def docker_compose_command(self):
        """
        Returns command parts used for the docker compose commands

        Returns
        -------
        list[str]
            The docker compose command parts
        """
        docker_compose_cmd = self.docker_cmd_comment
        for file in self.compose_file_names:
            docker_compose_cmd += ["-f", file]
        if self.env_file:
            docker_compose_cmd += ["--env-file", self.env_file]
        return docker_compose_cmd


@pytest.mark.integration
@pytest.fixture()
def integration_link():
    return AIOHttpLink(endpoint_url="http://localhost:5454/graphql")


@pytest.mark.integration
@pytest.fixture(scope="session")
def environment():
    with DockerV2Compose(
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
