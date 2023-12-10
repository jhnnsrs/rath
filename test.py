from rath.links.auth import ComposedAuthLink
from rath.links.aiohttp import AIOHttpLink
from rath.links.graphql_ws import GraphQLWSLink
from rath.links import compose, split

from rath import Rath


async def aload_token() -> str:
    """Loads the token from the environment"""
    return "SERVER_TOKEN"


auth = ComposedAuthLink(token_loader=aload_token)
link = AIOHttpLink(endpoint_url="https://countries.trevorblades.com/")
ws = GraphQLWSLink(ws_endpoint_url="wss://countries.trevorblades.com/")  #


end_link = split(link, ws, lambda op: op.node.operation == "SUBSCRIPTION")
with_auth = compose(auth, end_link)

with Rath(link=with_auth) as rath:
    query = """query {
        countries {
            native
            capital
        }
        }

    """

    result = rath.query(query)  # uses the http link
    print(result)

    subscription = """subscription {
        newCountry {
            native
            capital
        }
        }

    """

    for i in rath.subscribe(subscription):  # uses the ws link
        print(i)  # will fail because the server does not support subscriptions
