""" Provides  a fakts implementaiton of the aiohttp link"""

from typing import Any, Dict, Optional
from pydantic import BaseModel
from fakts.fakts import Fakts
from rath.links.aiohttp import AIOHttpLink
from rath.operation import Operation


class AioHttpConfig(BaseModel):
    """AioHttpConfig

    AioHttpConfig is a Fakt that can be used to configure the aiohttp client.
    """

    endpoint_url: str
    """The endpoint url to use for the aiohttp client"""


class FaktsAIOHttpLink(AIOHttpLink):
    """FaktsAIOHttpLink

    A FaktsAIOHttpLink is a link that retrieves the configuration
    from a sorounding fakts context.

    """

    fakts: Fakts
    """The fakts context to use for configuration"""
    endpoint_url: Optional[str]  # type: ignore

    fakts_group: str
    """ The fakts group within the fakts context to use for configuration """

    _old_fakt: Optional[Dict[str, Any]] = None

    def configure(self, fakt: AioHttpConfig) -> None:
        """Configure the link with the given fakt"""
        self.endpoint_url = fakt.endpoint_url

    async def aconnect(self, operation: Operation) -> None:
        """Connects the link to the server

        This method will retrieve the configuration from the fakts context,
        and configure the link with it. Before connecting, it will check if the
        configuration has changed, and if so, it will reconfigure the link.
        """
        if self.fakts.has_changed(self._old_fakt, self.fakts_group):
            self._old_fakt = await self.fakts.aget(self.fakts_group)
            assert self._old_fakt is not None, "Fakt should not be None"
            self.configure(AioHttpConfig(**self._old_fakt))

        return await super().aconnect(operation)
