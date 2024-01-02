from typing import Any, Dict, Optional
from pydantic import BaseModel
from fakts.fakts import Fakts
from rath.links.subscription_transport_ws import SubscriptionTransportWsLink
from rath.operation import Operation


class WebsocketHttpConfig(BaseModel):
    """WebsocketHttpConfig"""

    ws_endpoint_url: str


class FaktsWebsocketLink(SubscriptionTransportWsLink):
    """FaktsWebsocketLink


    A FaktsWebsocketLink is a SubscriptionTransportWsLink that retrieves the configuration
    from a passed fakts context.

    """

    fakts: Fakts
    """The fakts context to use for configuration"""
    ws_endpoint_url: Optional[str]  # type: ignore
    fakts_group: str = "websocket"
    """ The fakts group within the fakts context to use for configuration """

    _old_fakt: Optional[Dict[str, Any]] = None

    def configure(self, fakt: WebsocketHttpConfig) -> None:
        """Configure the link with the given fakt"""
        self.ws_endpoint_url = fakt.ws_endpoint_url

    async def aconnect(self, operation: Operation) -> None:
        """Connects the link to the server

        This method will retrieve the configuration from the fakts context,
        and configure the link with it. Before connecting, it will check if the
        configuration has changed, and if so, it will reconfigure the link.
        """
        if self.fakts.has_changed(self._old_fakt, self.fakts_group):
            self._old_fakt = await self.fakts.aget(self.fakts_group)
            assert self._old_fakt is not None, "Fakt should not be None"
            self.configure(WebsocketHttpConfig(**self._old_fakt))

        return await super().aconnect(operation)
