import asyncio
from examples.api.schema import aget_capsules
from rath.rath import Rath
from rath.links.aiohttp import AIOHttpLink
from rath.links.auth import AuthTokenLink
from rath.links.compose import compose


async def token_loader():
    return ""


link = compose(
    AuthTokenLink(token_loader), AIOHttpLink("https://api.spacex.land/graphql/")
)


RATH = Rath(
    link=link,
    register=True,
)


async def main():

    capsules = await aget_capsules()
    print(capsules)


asyncio.run(main())
