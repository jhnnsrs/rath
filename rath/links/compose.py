from os import link
from typing import List
from rath.links.base import Link, TerminatingLink
from rath.operation import Operation


class ComposedLink(TerminatingLink):
    def __init__(self, links: List[Link]):
        assert isinstance(
            links[-1], TerminatingLink
        ), "Last link must be a TerminatingLink"
        self.links = links
        self.first_link = links[0]

    def __call__(self, rath):
        for i in range(len(self.links) - 1):
            self.links[i](rath, self.links[i + 1])

        self.links[-1](rath)  # last one gets only rath

    async def aconnect(self):
        for link in self.links:
            await link.aconnect()

    async def aquery(self, operation: Operation):
        return await self.first_link.aquery(operation)

    async def asubscribe(self, operation: Operation):
        for result in await self.first_link.asubscribe(operation):
            yield result


def compose(*links: List[Link]) -> ComposedLink:
    """
    Composes a list of Links into a single Link.
    """

    return ComposedLink(links)
