from typing import Any, Dict, Optional
from fakts.fakt.base import Fakt
from fakts.fakts import get_current_fakts
from rath.links.aiohttp import AIOHttpLink


class AioHttpConfig(Fakt):
    endpoint_url: str

    class Config:
        group = "aiohttp"


class FaktsAIOHttpLink(AIOHttpLink):
    endpoint_url: Optional[str]
    fakts_group: str
    fakt: Optional[AioHttpConfig]

    _old_fakt: Dict[str, Any] = None

    def configure(self, fakt: AioHttpConfig) -> None:
        self.endpoint_url = fakt.endpoint_url

    async def aconnect(self):
        fakts = get_current_fakts()

        if fakts.has_changed(self._old_fakt, self.fakts_group):
            self._old_fakt = await fakts.aget(self.fakts_group)
            self.configure(AioHttpConfig(**self._old_fakt))

        return await super().aconnect()
