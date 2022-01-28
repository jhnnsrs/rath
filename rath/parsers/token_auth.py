from rath.operation import Operation

import io
import aiohttp
from typing import AsyncGenerator

from rath.parsers.base import Parser

FILE_CLASSES = (
    io.IOBase,
    aiohttp.StreamReader,
    AsyncGenerator,
)
from typing import Any, Callable, Dict, Tuple, Type


class TokenParser(Parser):
    def __init__(self, token="", token_func=None) -> None:
        super().__init__()
        self.token = token
        self.token_func = token_func

    async def aconnect(self):
        return await super().aconnect()

    def parse(self, operation: Operation) -> Operation:
        operation.context.headers["Authorization"] = f"Bearer {self.token}"
        return operation
