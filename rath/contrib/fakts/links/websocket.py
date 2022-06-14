from typing import Optional
from fakts.config.base import Config
from rath.links.aiohttp import AIOHttpLink
from rath.links.auth import AuthTokenLink
from rath.links.websockets import WebSocketLink
from herre import current_herre


class AioHttpConfig(Config):
    ws_endpoint_url: str

    class Config:
        group = "aiohttp"


class FaktsWebsocketLink(WebSocketLink):
    ws_endpoint_url: Optional[str]
    fakts_group: str

    async def aconnect(self):
        print("CONNECTING")
        herre = current_herre.get()
        config = await AioHttpConfig.from_fakts(self.fakts_group)
        self.ws_endpoint_url = config.ws_endpoint_url
        self.token_loader = herre.aget_token
        return await super().aconnect()
