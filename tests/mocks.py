from rath.links.testing.mock import AsyncMockResolver
import asyncio


class QueryAsync(AsyncMockResolver):
    """Async Test"""

    async def resolve_beast(self, _):
        """Resolves a beast

        Args:
            operation (Operation): _description_

        Returns:
            _type_: _description_
        """
        return {"id": "1", "legs": 1}

    async def resolve_beasts(self, _):
        """Resolves Fake beasts

        Args:
            operation (Operation): _description_

        Returns:
            _type_: _description_
        """
        return [
            {"id": "1", "legs": 1, "commonName": "Katze"},
            {"id": "2", "legs": 2, "commonName": "Hund"},
        ]


class MutationAsync(AsyncMockResolver):
    """Async Test"""

    # pylint: disable=invalid-name
    async def resolve_createBeast(self, _):
        """Resolves creating a beast"""
        return {"id": "1", "legs": 1}


class SubscriptionAsync(AsyncMockResolver):
    """Async Test"""

    # pylint: disable=invalid-name
    async def resolve_watchBeast(self, _):
        """Resolves watching a beast

        Args:
            operation (Operation): _description_

        Yields:
            _type_: _description_
        """
        for i in range(0, 10):
            await asyncio.sleep(0.001)
            yield {"id": "1", "legs": i}
