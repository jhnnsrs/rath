from arkitekt.messages import T
from rath.rath import Rath


class FaktsRath(Rath):
    async def aconnect(self: T) -> T:

        return await super().aconnect()
