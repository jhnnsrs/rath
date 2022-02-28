from rath.links.context import SwitchAsyncLink
from rath.links.errors import LinkNotConnectedError
from rath.links.validate import ValidatingLink, ValidationError
from rath.operation import Operation, opify
import pytest
from rath.links import compose
from rath.links.testing.mock import AsyncMockLink, AsyncMockResolver
from rath.links.testing.statefulmock import AsyncStatefulMockLink
from rath import Rath
from tests.mocks import MutationAsync, QueryAsync, SubscriptionAsync
from koil import Koil


@pytest.fixture()
def mock_link():
    return AsyncMockLink(
        query_resolver=QueryAsync(),
        mutation_resolver=MutationAsync(),
        subscription_resolver=SubscriptionAsync(),
    )


@pytest.fixture()
def stateful_mocklink():
    return AsyncStatefulMockLink(
        query_resolver=QueryAsync(),
        mutation_resolver=MutationAsync(),
        subscription_resolver=SubscriptionAsync(),
    )


@pytest.fixture()
def simple_rath(mock_link):
    return Rath(compose(SwitchAsyncLink(), mock_link))


@pytest.fixture()
def stateful_rath(stateful_mocklink):
    return Rath(compose(SwitchAsyncLink(), stateful_mocklink))


async def test_bypass(simple_rath):

    x = await simple_rath.aexecute(
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

    with pytest.raises(LinkNotConnectedError):
        x = await stateful_rath.aexecute(
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
        x = await stateful_rath.aexecute(
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
        x = stateful_rath.execute(
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
        x = stateful_rath.execute(
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
        x = stateful_rath.execute(
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
            x = stateful_rath.execute(
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
            x = stateful_rath.execute(
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

    stateful_rath.connect()

    x = stateful_rath.execute(
        """
            query {
                beast(id: "1") {
                    binomial
                }
            }
        """
    )

    assert x.data, "No data received"

    x = stateful_rath.execute(
        """
            query {
                beast(id: "1") {
                    binomial
                }
            }
        """
    )

    assert x.data, "No data received"

    stateful_rath.disconnect()


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

    rath = Rath(compose(SwitchAsyncLink(), mock_link))

    rath.execute(
        """
        query {
            beast(id: "1") {
                binomial
            }
        }
    """
    )


def test_switch_sync(mock_link):

    rath = Rath(compose(SwitchAsyncLink(), mock_link))

    rath.execute(
        """
        query {
            beast(id: "1") {
                binomial
            }
        }
    """
    )
