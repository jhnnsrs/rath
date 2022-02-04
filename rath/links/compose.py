import asyncio
from os import link
from typing import List
from rath.links.base import ContinuationLink, Link, TerminatingLink
from rath.operation import Operation


class ComposedLink(TerminatingLink):
    def __init__(self, links: List[Link]):
        assert isinstance(
            links[-1], TerminatingLink
        ), "Last link must be a TerminatingLink"
        for link in links[:-1]:
            assert isinstance(
                link, ContinuationLink
            ), f"All but the last must be ContinuationLinks: check {link}"
        self.links = links
        self.first_link = links[0]

    def __call__(self, rath):
        for i in range(len(self.links) - 1):
            self.links[i](rath, self.links[i + 1])

        self.links[-1](rath)  # last one gets only rath

    async def aconnect(self):
        return await asyncio.gather(*[link.aconnect() for link in self.links])

    async def aquery(self, operation: Operation):
        return await self.first_link.aquery(operation)

    async def asubscribe(self, operation: Operation):
        for result in await self.first_link.asubscribe(operation):
            yield result

    def query(self, operation: Operation):
        return self.first_link.query(operation)

    def subscribe(self, operation: Operation):
        for result in self.first_link.subscribe(operation):
            yield result


def compose(*links: List[Link]) -> ComposedLink:
    """
    Composes a list of Links into a single Link.
    """

    return ComposedLink(links)
