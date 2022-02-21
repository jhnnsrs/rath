from rath.links.validate import ValidatingLink, ValidationError
from rath.operation import Operation, opify
import pytest
from rath.links import compose
from rath.links.testing.mock import AsyncMockLink, AsyncMockResolver
from rath import Rath

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
    async def resolve_beast(self, operation: Operation):
        return {"id": "1", "legs": 1}


class MutationAsync(AsyncMockResolver):
    pass

    async def resoplve_createBeast(self, operation: Operation):
        return {
            "id": operation.variables["id"],
            "name": "John Doe",
            "email": "john.doe@gmail.com",
        }


@pytest.fixture()
def mock_link():
    return AsyncMockLink(query_resolver=QueryAsync(), mutation_resolver=MutationAsync())


async def test_validation(mock_link):

    link = ValidatingLink(schema_dsl=schema)

    rath = Rath(compose(link, mock_link))

    await rath.aexecute(
        """
        query {
            beast(id: "1") {
                binomial
            }
        }
    """
    )


async def test_validation(mock_link):

    link = ValidatingLink(schema_dsl=schema)

    rath = Rath(compose(link, mock_link))

    await rath.aexecute(
        """
        query {
            beast(id: "1") {
                binomial
            }
        }
    """
    )


async def test_validation(mock_link):

    link = ValidatingLink(schema_dsl=schema)

    rath = Rath(compose(link, mock_link))

    with pytest.raises(ValidationError):
        await rath.aexecute(
            """
            query {
                beast(leg: 1) {
                    binomial
                }
            }
            """
        )
