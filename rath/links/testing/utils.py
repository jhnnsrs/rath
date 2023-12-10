from rath.links.base import AsyncTerminatingLink
from rath.operation import opify, GraphQLResult


async def run_basic_query(link: AsyncTerminatingLink) -> GraphQLResult:  # type: ignore
    """Run a basic query against the given link"""
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
