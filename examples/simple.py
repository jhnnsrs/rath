from rath import Rath


from rath.links.aiohttp import AIOHttpLink
from rath import Rath

link = AIOHttpLink(endpoint_url="https://countries.trevorblades.com/")


with Rath(link=link) as rath:
    query = """query {
        countries {
            native
            capital
        }
        }

    """

    result = rath.query(query)
    print(result)