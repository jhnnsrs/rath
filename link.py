import asyncio
from examples.api.schema import aget_random_rep, get_random_rep
from rath.parsers.file import FileParser
from rath.rath import Rath
from rath.links.aiohttp import AIOHttpLink
from rath.links.token import TokenContinuationLink
from rath.links.compose import compose


link = compose(TokenContinuationLink(), AIOHttpLink("http://localhost:8080/graphql"))


RATH = Rath(
    parsers=[FileParser()],
    link=link,
    register=True,
)


async def main():

    johannes = await aget_random_rep()
    print(johannes.store)


def hallo():
    print(get_random_rep())


hallo()
asyncio.run(main())
