from typing import Any, Dict, Optional
from fakts.fakt.base import Fakt
from fakts.fakts import get_current_fakts, Fakts
from rath.links.httpx import HttpxLink


class FaltsHttpXConfig(Fakt):
    endpoint_url: str

    class Config:
        group = "aiohttp"


class FaktsHttpXLink(HttpxLink):
    endpoint_url: Optional[str]
    fakts_group: str
    fakt: Optional[FaltsHttpXConfig]
    fakts: Fakts

    _old_fakt: Dict[str, Any] = None

    def configure(self, fakt: FaltsHttpXConfig) -> None:
        self.endpoint_url = fakt.endpoint_url

    async def aconnect(self, operation):
        if self.fakts.has_changed(self._old_fakt, self.fakts_group):
            self._old_fakt = await self.fakts.aget(self.fakts_group)
            self.configure(FaltsHttpXConfig(**self._old_fakt))

        return await super().aconnect(operation)
