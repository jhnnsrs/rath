from rath import Rath
from rath.links.timeout import TimeoutLink
from rath.links.testing.never_succeeding_link import NeverSucceedingLink
import pytest



async def test_timeout():
    
    rath = Rath(
        link=[
            TimeoutLink(timeout=1),
            NeverSucceedingLink()
        ]
    )
    
    with pytest.raises(TimeoutError):
        async with rath:
            await rath.aquery(
                """
                query {
                    beast(id: "1") {
                        binomial
                    }
                }
            """
            )
   