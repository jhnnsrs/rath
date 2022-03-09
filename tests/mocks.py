from rath.links.testing.mock import AsyncMockLink, AsyncMockResolver
from rath.operation import Operation
import asyncio


class QueryAsync(AsyncMockResolver):
    async def resolve_beast(self, operation: Operation):
        return {"id": "1", "legs": 1}

    async def resolve_beasts(self, operation: Operation):
        return [
            {"id": "1", "legs": 1, "commonName": "Katze"},
            {"id": "2", "legs": 2, "commonName": "Hund"},
        ]


class MutationAsync(AsyncMockResolver):
    pass

    async def resoplve_createBeast(self, operation: Operation):
        return {"id": "1", "legs": 1}


class SubscriptionAsync(AsyncMockResolver):
    pass

    async def resolve_watchBeast(self, operation: Operation):
        for i in range(0, 10):
            await asyncio.sleep(0.001)
            yield {"id": "1", "legs": i}
