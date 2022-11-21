""" Provides  a fakts implementaiton of the aiohttp link"""

from typing import Any, Dict, Optional
from fakts.fakt import Fakt
from fakts.fakts import get_current_fakts
from rath.links.aiohttp import AIOHttpLink


class AioHttpConfig(Fakt):
    """AioHttpConfig

    AioHttpConfig is a Fakt that can be used to configure the aiohttp client.
    """

    endpoint_url: str


class FaktsAIOHttpLink(AIOHttpLink):
    """FaktsAIOHttpLink

    A FaktsAIOHttpLink is a link that retrieves the configuration
    from a sorounding fakts context.

    """

    endpoint_url: Optional[str]

    fakts_group: str
    """ The fakts group within the fakts context to use for configuration """

    _old_fakt: Dict[str, Any] = None

    def configure(self, fakt: AioHttpConfig) -> None:
        """Configure the link with the given fakt"""
        self.endpoint_url = fakt.endpoint_url

    async def aconnect(self):
        fakts = get_current_fakts()

        if fakts.has_changed(self._old_fakt, self.fakts_group):
            self._old_fakt = await fakts.aget(self.fakts_group)
            self.configure(AioHttpConfig(**self._old_fakt))

        return await super().aconnect()
