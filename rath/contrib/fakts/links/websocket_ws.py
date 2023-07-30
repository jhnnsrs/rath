from typing import Any, Dict, Optional

from fakts.fakt.base import Fakt
from fakts.fakts import get_current_fakts
from herre import current_herre
from rath.links.websocket_ws import WebSocketWsLink


class WebsocketHttpConfig(Fakt):
    ws_endpoint_url: str

    class Config:
        group = "aiohttp"


class FaktsWebsocketWsLink(WebSocketWsLink):
    ws_endpoint_url: Optional[str]
    fakts_group: str = "websocket"

    _old_fakt: Dict[str, Any] = {}

    def configure(self, fakt: WebsocketHttpConfig) -> None:
        self.ws_endpoint_url = fakt.ws_endpoint_url
        self.build_initial_payload = self._payload_builder

    async def _payload_builder(self):
        return {"token": current_herre.get().aget_token()}

    async def aconnect(self):
        fakts = get_current_fakts()

        if fakts.has_changed(self._old_fakt, self.fakts_group):
            self._old_fakt = await fakts.aget(self.fakts_group)
            self.configure(WebsocketHttpConfig(**self._old_fakt))

        return await super().aconnect()
