from typing import Any, Dict, Optional

from pydantic import BaseModel
from fakts.fakts import Fakts
from rath.links.graphql_ws import GraphQLWSLink


class WebsocketHttpConfig(BaseModel):
    """A WebsocketHttpConfig is a Fakt that can be used to configure the aiohttp client."""

    ws_endpoint_url: str


class FaktsGraphQLWSLink(GraphQLWSLink):
    """FaktsGraphQLWSLink


    A FaktsGraphQLWSLink is a GraphQLWSLink that retrieves the configuration
    from a passed fakts context.

    """

    fakts: Fakts
    """The fakts context to use for configuration"""
    ws_endpoint_url: Optional[str]  # type: ignore
    fakts_group: str = "websocket"
    """ The fakts group within the fakts context to use for configuration """

    _old_fakt: Dict[str, Any] = {}

    def configure(self, fakt: WebsocketHttpConfig) -> None:
        """Configure the link with the given fakt"""
        self.ws_endpoint_url = fakt.ws_endpoint_url

    async def aconnect(self, operation: Any) -> None:
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
