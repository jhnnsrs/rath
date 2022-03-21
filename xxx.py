from rath.links.testing.mock import AsyncMockResolver
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


print(QueryAsync().to_dict())
