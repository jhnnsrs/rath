import asyncio
from pydantic import BaseModel
from fakts.fakts import Fakts, current_fakts
from rath.links.aiohttp import AIOHttpLink
from rath.operation import Operation


class FaktsAioHttpLinkConfig(BaseModel):
    endpoint_url: str


class FaktsAioHttpLink(AIOHttpLink):
    def __init__(self, *args, fakts: Fakts = None, fakts_key="rath", **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._lock = None
        self.fakts = fakts or current_fakts.get()
        self.fakts_key = fakts_key
        self.config = None

    def configure(self, fakts: FaktsAioHttpLinkConfig):
        self.url = fakts.endpoint_url
        self.config = fakts

    async def aquery(self, operation: Operation, **kwargs) -> None:
        if not self._lock:
            self._lock = asyncio.Lock()

        async with self._lock:
            if not self.config:
                fakts = await self.fakts.aget(self.fakts_key)
                self.configure(FaktsAioHttpLinkConfig(**fakts))

        return await super().aquery(operation, **kwargs)
