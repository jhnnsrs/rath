from rath.links.testing.mock import AsyncMockLink, AsyncMockResolver
from rath.operation import Operation
import asyncio

schema = """
type Beast {
    "ID of beast (taken from binomial initial)"
    id: ID
    "number of legs beast has"
    legs: Int
    "a beast's name in Latin"
    binomial: String
    "a beast's name to you and I"
    commonName: String
    "taxonomy grouping"
    taxClass: String
    "a beast's prey"
    eats: [ Beast ]
    "a beast's predators"
    isEatenBy: [ Beast ]
}

type Query {
    beasts: [Beast]
    beast(id: ID!): Beast
    calledBy(commonName: String!): [Beast]
}

type Mutation {
    createBeast(id: ID!, legs: Int!, binomial: String!, 
        commonName: String!, taxClass: String!, eats: [ ID ]
        ): Beast 
	}

type Subscription {
    watchBeast(id: ID!) : Beast
	}
"""


class QueryAsync(AsyncMockResolver):
    async def resolve_beast(self, operation: Operation):
        return {"id": "1", "legs": 1}


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
