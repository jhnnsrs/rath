from typing import Any, Dict, Optional

from fakts.fakt.base import Fakt
from fakts.fakts import Fakts
from herre import current_herre
from rath.links.subscription_transport_ws import SubscriptionTransportWsLink


class WebsocketHttpConfig(Fakt):
    ws_endpoint_url: str

    class Config:
        group = "aiohttp"


class FaktsWebsocketLink(SubscriptionTransportWsLink):
    fakts: Fakts
    ws_endpoint_url: Optional[str]
    fakts_group: str = "websocket"

    _old_fakt: Dict[str, Any] = {}

    def configure(self, fakt: WebsocketHttpConfig) -> None:
        self.ws_endpoint_url = fakt.ws_endpoint_url
        self.token_loader = current_herre.get().aget_token

    async def aconnect(self, operation):
        if self.fakts.has_changed(self._old_fakt, self.fakts_group):
            self._old_fakt = await self.fakts.aget(self.fakts_group)
            self.configure(WebsocketHttpConfig(**self._old_fakt))

        return await super().aconnect(operation)
