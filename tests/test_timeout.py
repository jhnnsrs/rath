from rath import Rath
from rath.links.timeout import TimeoutLink
from rath.links.testing.never_succeeding_link import NeverSucceedingLink
from rath.links.testing.direct_succeeding_link import DirectSucceedingLink
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
            
            
async def test_should_suceed_timeout():
    rath = Rath(
        link=[
            TimeoutLink(timeout=2),
            DirectSucceedingLink()
        ]
    )
    
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
   