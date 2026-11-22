import pytest

from graphql import OperationType
from rath import Rath
from rath.links import split
from rath.links.testing.mock import AsyncMockLink
from rath.links.testing.statefulmock import AsyncStatefulMockLink

from .mocks import MutationAsync, QueryAsync, SubscriptionAsync


@pytest.fixture()
def mock_link_left() -> AsyncMockLink:
    return AsyncMockLink(
        query_resolver=QueryAsync().to_dict(),
        mutation_resolver=MutationAsync().to_dict(),
    )


@pytest.fixture()
def mock_link_right() -> AsyncMockLink:
    return AsyncMockLink(subscription_resolver=SubscriptionAsync().to_dict())


@pytest.fixture()
def stateful_mock_link() -> AsyncStatefulMockLink:
    return AsyncStatefulMockLink(
        query_resolver=QueryAsync().to_dict(),
        mutation_resolver=MutationAsync().to_dict(),
    )


async def test_aquery(
    mock_link_left: AsyncMockLink, mock_link_right: AsyncMockLink
) -> None:
    rath = Rath(
        link=split(
            mock_link_left,
            mock_link_right,
            lambda o: o.node.operation != OperationType.SUBSCRIPTION,
        )
    )

    async with rath as r:
        await r.aquery(
            """
            query {
                beast(id: "1") {
                    binomial
                }
            }
        """
        )


async def test_stateful_mock(stateful_mock_link: AsyncStatefulMockLink) -> None:
    async with Rath(link=stateful_mock_link) as rath:
        await rath.aquery(
            """
            query {
                beast(id: "1") {
                    binomial
                }
            }
        """,
            timeout=1,
        )


def test_stateful_mock_sync(stateful_mock_link: AsyncStatefulMockLink) -> None:
    with Rath(link=stateful_mock_link) as rath:
        rath.query(
            """
                    query {
                        beast(id: "1") {
                            binomial
                        }
                    }
                """
        )


async def test_asubscribe(
    mock_link_left: AsyncMockLink, mock_link_right: AsyncMockLink
) -> None:
    rath = Rath(
        link=split(
            mock_link_left,
            mock_link_right,
            lambda o: o.node.operation != OperationType.SUBSCRIPTION,
        )
    )

    async with rath as r:
        async for ev in r.asubscribe(
            """
            subscription {
                watchBeast(id: "1") {
                    legs
                }
            }
            """
        ):
            x = ev

        assert x.data["watchBeast"]["legs"] == 9
