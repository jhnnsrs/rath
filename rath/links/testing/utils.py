from rath.links.base import AsyncTerminatingLink
from rath.operation import Operation, opify
from graphql import parse


async def run_basic_query(link: AsyncTerminatingLink):
    async with link:
        async for i in link.aexecute(
            operation=opify(
                """
                    query {
                        hello
                    }
                    """
            )
        ):
            return i
