from typing import Awaitable, Callable, Optional
from herre.herre import Herre
from rath.links.aiohttp import AIOHttpLink
from rath.links.auth import AuthTokenLink
from herre import current_herre


class HerreAuthLink(AuthTokenLink):
    herre: Optional[Herre]
    token_loader: Optional[Callable[[], Awaitable[str]]]
    token_refresher: Optional[Callable[[], Awaitable[str]]]

    async def aconnect(self):
        self.herre = self.herre or current_herre.get()
        self.token_loader = self.herre.aget_token
        self.token_refresher = self.herre.arefresh_token
        return await super().aconnect()
