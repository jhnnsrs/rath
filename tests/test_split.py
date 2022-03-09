from graphql import OperationType
from rath.links.context import SwitchAsyncLink
from rath.links.testing.statefulmock import AsyncStatefulMockLink
from rath.links.validate import ValidatingLink, ValidationError
from rath.operation import Operation, opify
import pytest
from rath.links import compose, split
from tests.mocks import *
from rath import Rath
import asyncio


@pytest.fixture()
def mock_link_left():
    return AsyncMockLink(query_resolver=QueryAsync(), mutation_resolver=MutationAsync())


@pytest.fixture()
def mock_link_right():
    return AsyncMockLink(subscription_resolver=SubscriptionAsync())


@pytest.fixture()
def stateful_mock_link():
    return AsyncStatefulMockLink(
        query_resolver=QueryAsync(), mutation_resolver=MutationAsync()
    )


async def test_aquery(mock_link_left, mock_link_right):

    rath = Rath(
        split(
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

    async with Rath(stateful_mock_link) as rath:
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
        compose(
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
        split(
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
