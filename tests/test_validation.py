from rath.links.validate import ValidatingLink, ValidationError
from rath.operation import Operation
import pytest
from rath.links import compose
from rath.links.testing.mock import AsyncMockLink, AsyncMockResolver
from rath import Rath
from .utils import build_relative_glob

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
"""


class QueryAsync(AsyncMockResolver):
    @staticmethod
    async def resolve_beast(operation: Operation):
        return {"id": "1", "legs": 1}


class MutationAsync(AsyncMockResolver):
    @staticmethod
    async def resolve_createBeast(operation: Operation):
        return {
            "id": operation.variables["id"],
            "name": "John Doe",
            "email": "john.doe@gmail.com",
        }


@pytest.fixture()
def mock_link():
    return AsyncMockLink(
        query_resolver=QueryAsync().to_dict(),
        mutation_resolver=MutationAsync().to_dict(),
    )


async def test_validation(mock_link):
    link = ValidatingLink(schema_glob=build_relative_glob("/schemas/beasts.graphql"))

    async with Rath(link=compose(link, mock_link)) as r:
        await r.aquery(
            """
            query {
                beast(id: "1") {
                    binomial
                }
            }
        """
        )


async def test_validation_error(mock_link):
    link = ValidatingLink(schema_dsl=schema)

    rath = Rath(link=compose(link, mock_link))
    r = await rath.aenter()

    with pytest.raises(ValidationError):
        await r.aquery(
            """
            query {
                beast(leg: 1) {
                    binomial
                }
            }
            """
        )

    await rath.aexit()
