import pytest
from koil import Koil

from rath import Rath
from rath.links import compose
from rath.links.testing.mock import AsyncMockLink
from rath.links.testing.statefulmock import AsyncStatefulMockLink

from .mocks import MutationAsync, QueryAsync, SubscriptionAsync


@pytest.fixture()
def mock_link() -> AsyncMockLink:
    return AsyncMockLink(
        query_resolver=QueryAsync().to_dict(),
        mutation_resolver=MutationAsync().to_dict(),
        subscription_resolver=SubscriptionAsync().to_dict(),
    )


@pytest.fixture()
def stateful_mocklink() -> AsyncStatefulMockLink:
    return AsyncStatefulMockLink(
        query_resolver=QueryAsync().to_dict(),
        mutation_resolver=MutationAsync().to_dict(),
        subscription_resolver=SubscriptionAsync().to_dict(),
    )


@pytest.fixture()
def simple_rath(mock_link: AsyncMockLink) -> Rath:
    return Rath(link=mock_link)


@pytest.fixture()
def stateful_rath(stateful_mocklink: AsyncStatefulMockLink) -> Rath:
    return Rath(link=stateful_mocklink)


async def test_bypass(simple_rath: Rath) -> None:
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


async def test_stateful_link_execution(stateful_rath: Rath) -> None:
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


def test_stateful_link_execution_sync(stateful_rath: Rath) -> None:
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


def test_stateful_link_execution_sync_no_sideffects(stateful_rath: Rath) -> None:
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


def test_stateful_link_subscription_sync_no_sideffects(stateful_rath: Rath) -> None:
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


def test_stateful_link_execution_sync_same_koil(stateful_rath: Rath) -> None:
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


def test_stateful_link_subscription_sync_same_koil(stateful_rath: Rath) -> None:
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


def test_query_sinc(mock_link: AsyncMockLink) -> None:
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


def test_switch_sync(mock_link: AsyncMockLink) -> None:
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
