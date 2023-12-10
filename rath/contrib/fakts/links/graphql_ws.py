from typing import Any, Dict, Optional

from fakts.fakt.base import Fakt
from fakts.fakts import Fakts
from rath.links.graphql_ws import GraphQLWSLink


class WebsocketHttpConfig(Fakt):
    ws_endpoint_url: str

    class Config:
        group = "aiohttp"


class FaktsGraphQLWSLink(GraphQLWSLink):
    fakts: Fakts
    ws_endpoint_url: Optional[str] # type: ignore
    fakts_group: str = "websocket"

    _old_fakt: Dict[str, Any] = {}

    def configure(self, fakt: WebsocketHttpConfig) -> None:
        self.ws_endpoint_url = fakt.ws_endpoint_url

    async def aconnect(self, operation: Any):
        if self.fakts.has_changed(self._old_fakt, self.fakts_group):
            self._old_fakt = await self.fakts.aget(self.fakts_group)
            assert self._old_fakt is not None, "Fakt should not be None"
            self.configure(WebsocketHttpConfig(**self._old_fakt))

        return await super().aconnect(operation)
