




from pydantic import BaseModel
from herre.herre import Herre, get_current_herre
from rath.links.auth import AuthTokenLink



class HerreAuthTokenLink(AuthTokenLink):


    def __init__(self, *args, herre: Herre = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.herre = herre or get_current_herre()
        self.config = None

    async def aconnect(self) -> None:
        self.token_loader = self.herre.aget_token
        return await super().aconnect()
