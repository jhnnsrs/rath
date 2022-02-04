from pydantic import BaseModel
from fakts.fakts import Fakts, get_current_fakts
from rath.links.aiohttp import AIOHttpLink


class FaktsAioHttpLinkConfig(BaseModel):
    endpoint_url: str


class FaktsAioHttpLink(AIOHttpLink):


    def __init__(self, *args, fakts: Fakts = None, fakts_key="rath", **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fakts = fakts or get_current_fakts()
        self.fakts_key = fakts_key
        self.config = None


    def configure(self, fakts: FaktsAioHttpLinkConfig):
        self.url = fakts.endpoint_url


    async def aconnect(self) -> None:
        if not self.config:
            self.fakts = await self.fakts.aget(self.fakts_key)
            self.configure(FaktsAioHttpLinkConfig(**self.fakts))

        return await super().aconnect()
