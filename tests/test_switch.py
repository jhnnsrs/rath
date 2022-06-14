from rath.errors import NotConnectedError, NotEnteredError
import pytest
from rath.links import compose
from rath.links.testing.mock import AsyncMockLink
from rath.links.testing.statefulmock import AsyncStatefulMockLink
from rath import Rath
from .mocks import MutationAsync, QueryAsync, SubscriptionAsync
from koil import Koil


@pytest.fixture()
def mock_link():
    return AsyncMockLink(
        query_resolver=QueryAsync().to_dict(),
        mutation_resolver=MutationAsync().to_dict(),
        subscription_resolver=SubscriptionAsync().to_dict(),
    )


@pytest.fixture()
def stateful_mocklink():
    return AsyncStatefulMockLink(
        query_resolver=QueryAsync().to_dict(),
        mutation_resolver=MutationAsync().to_dict(),
        subscription_resolver=SubscriptionAsync().to_dict(),
    )


@pytest.fixture()
def simple_rath(mock_link):
    return Rath(link=mock_link)


@pytest.fixture()
def stateful_rath(stateful_mocklink):
    return Rath(link=stateful_mocklink)


async def test_bypass(simple_rath):

    async with simple_rath:
        x = await simple_rath.aquery(
            """
            query {
                beast(id: "1") {
                    binomial
                }
            }
        """
        )
        assert x.data, "No data"


async def test_link_not_connected_exception(stateful_rath):

    with pytest.raises(NotEnteredError):
        x = await stateful_rath.aquery(
            """
            query {
                beast(id: "1") {
                    binomial
                }
            }
        """
        )


async def test_stateful_link_execution(stateful_rath):

    async with stateful_rath:
        x = await stateful_rath.aquery(
            """
            query {
                beast(id: "1") {
                    binomial
                }
            }
        """
        )

        assert x.data, "No data received"


def test_stateful_link_execution_sync(stateful_rath):

    with stateful_rath:
        x = stateful_rath.query(
            """
            query {
                beast(id: "1") {
                    binomial
                }
            }
        """
        )

        assert x.data, "No data received"


def test_stateful_link_execution_sync_no_sideffects(stateful_rath):

    with stateful_rath:
        x = stateful_rath.query(
            """
            query {
                beast(id: "1") {
                    binomial
                }
            }
        """
        )

        assert x.data, "No data received"

    with stateful_rath:
        x = stateful_rath.query(
            """
            query {
                beast(id: "1") {
                    binomial
                }
            }
        """
        )

        assert x.data, "No data received"


def test_stateful_link_subscription_sync_no_sideffects(stateful_rath):

    with stateful_rath:
        for x in stateful_rath.subscribe(
            """
                            subscription {
                        watchBeast(id: "1") {
                            legs
                        }
                    }
                """
        ):
            assert x.data, "No data received"

    with stateful_rath:
        for x in stateful_rath.subscribe(
            """
                            subscription {
                        watchBeast(id: "1") {
                            legs
                        }
                    }
                """
        ):
            assert x.data, "No data received"


def test_stateful_link_execution_sync_same_koil(stateful_rath):

    with Koil():

        with stateful_rath:
            x = stateful_rath.query(
                """
                query {
                    beast(id: "1") {
                        binomial
                    }
                }
            """
            )

            assert x.data, "No data received"

        with stateful_rath:
            x = stateful_rath.query(
                """
                query {
                    beast(id: "1") {
                        binomial
                    }
                }
            """
            )

            assert x.data, "No data received"


def test_stateful_link_execution_sync_unsafe_connect(stateful_rath):

    stateful_rath.enter()

    x = stateful_rath.query(
        """
            query {
                beast(id: "1") {
                    binomial
                }
            }
        """
    )

    assert x.data, "No data received"

    x = stateful_rath.query(
        """
            query {
                beast(id: "1") {
                    binomial
                }
            }
        """
    )

    assert x.data, "No data received"

    stateful_rath.exit()


def test_stateful_link_subscription_sync_same_koil(stateful_rath):

    with Koil():

        with stateful_rath:
            for x in stateful_rath.subscribe(
                """
                            subscription {
                        watchBeast(id: "1") {
                            legs
                        }
                    }
                """
            ):
                assert x.data, "No data received"

        with stateful_rath:
            for x in stateful_rath.subscribe(
                """
                            subscription {
                        watchBeast(id: "1") {
                            legs
                        }
                    }
                """
            ):
                assert x.data, "No data received"


def test_query_sinc(mock_link):

    with Rath(link=mock_link) as rath:

        rath.query(
            """
            query {
                beast(id: "1") {
                    binomial
                }
            }
        """
        )


def test_switch_sync(mock_link):

    with Rath(link=compose(mock_link)) as rath:

        rath.query(
            """
            query {
                beast(id: "1") {
                    binomial
                }
            }
        """
        )
