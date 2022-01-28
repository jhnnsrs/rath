import asyncio
from examples.api.schema import aget_random_rep, get_random_rep
from rath.parsers.file import FileParser
from rath.rath import Rath
from rath.transports.aiohttp import AIOHttpTransport


test = """
query User {
    users {
        id
    }
}
"""


RATH = Rath(
    parsers=[FileParser()],
    transport=AIOHttpTransport("http://localhost:8080/graphql"),
    register=True,
)


async def main():

    johannes = await aget_random_rep()
    print(johannes)


def hallo():
    print(get_random_rep())


hallo()
asyncio.run(main())
