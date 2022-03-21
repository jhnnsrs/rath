from graphql import OperationType
from rath.links.context import SwitchAsyncLink
from rath.links.testing.mock import AsyncMockLink
from rath.links.testing.statefulmock import AsyncStatefulMockLink
import pytest
from rath.links import compose, split
from tests.mocks import *
from rath import Rath


@pytest.fixture()
def mock_link_left():
    return AsyncMockLink(
        query_resolver=QueryAsync().to_dict(),
        mutation_resolver=MutationAsync().to_dict(),
    )


@pytest.fixture()
def mock_link_right():
    return AsyncMockLink(subscription_resolver=SubscriptionAsync().to_dict())


@pytest.fixture()
def stateful_mock_link():
    return AsyncStatefulMockLink(
        query_resolver=QueryAsync().to_dict(),
        mutation_resolver=MutationAsync().to_dict(),
    )


async def test_aquery(mock_link_left, mock_link_right):

    rath = Rath(
        link=split(
            mock_link_left,
            mock_link_right,
            lambda o: o.node.operation != OperationType.SUBSCRIPTION,
        )
    )

    async with rath as r:
        await r.aexecute(
            """
            query {
                beast(id: "1") {
                    binomial
                }
            }
        """
        )


async def test_stateful_mock(stateful_mock_link):

    async with Rath(link=stateful_mock_link) as rath:
        await rath.aexecute(
            """
            query {
                beast(id: "1") {
                    binomial
                }
            }
        """,
            timeout=1,
        )


def test_stateful_mock_sync(stateful_mock_link):

    with Rath(
        link=compose(
            SwitchAsyncLink(),
            stateful_mock_link,
        )
    ) as rath:

        rath.execute(
            """
                    query {
                        beast(id: "1") {
                            binomial
                        }
                    }
                """
        )


async def test_asubscribe(mock_link_left, mock_link_right):

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
