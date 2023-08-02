from typing import Optional
from herre.herre import Herre
from rath.links.auth import AuthTokenLink
from herre import current_herre


class HerreAuthLink(AuthTokenLink):
    herre: Herre

    async def aload_token(self) -> str:
        herre = self.herre
        return await herre.aget_token()

    async def arefresh_token(self) -> str:
        herre = self.herre
        return await herre.arefresh_token()
