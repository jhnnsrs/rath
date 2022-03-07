from pydantic import BaseModel
from herre.herre import Herre, current_herre
from rath.links.auth import AuthTokenLink


class HerreAuthTokenLink(AuthTokenLink):
    def __init__(self, *args, herre: Herre = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.herre = herre or current_herre.get()
        self.token_loader = self.herre.aget_token
