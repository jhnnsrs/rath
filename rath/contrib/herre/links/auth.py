from herre.herre import Herre
from rath.links.auth import AuthTokenLink
from rath.operation import Operation


class HerreAuthLink(AuthTokenLink):
    """HerreAuthLink is a link that retrieves a token from herre and sends it to the next link."""

    herre: Herre

    async def aload_token(self, operation: Operation) -> str:
        """Retrieves the token from herre"""
        herre = self.herre
        return await herre.aget_token()

    async def arefresh_token(self, operation: Operation) -> str:
        """Refreshes the token from herre"""
        herre = self.herre
        return await herre.arefresh_token()
