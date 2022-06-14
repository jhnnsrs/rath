from typing import Optional
from fakts.config.base import Config
from rath.links.aiohttp import AIOHttpLink


class AioHttpConfig(Config):
    endpoint_url: str

    class Config:
        group = "aiohttp"


class FaktsAIOHttpLink(AIOHttpLink):
    endpoint_url: Optional[str]
    fakts_group: str

    async def aconnect(self):
        config = await AioHttpConfig.from_fakts(self.fakts_group)
        self.endpoint_url = config.endpoint_url
        return await super().aconnect()
