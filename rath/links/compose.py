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

    async def __aenter__(self):
        for link in self.links:
            await link.__aenter__()

    async def __aexit__(self, *args, **kwargs):
        for link in self.links:
            await link.__aexit__(*args, **kwargs)

    async def aquery(self, operation: Operation, **kwargs):
        return await self.first_link.aquery(operation)

    async def asubscribe(self, operation: Operation, **kwargs):
        async for result in self.first_link.asubscribe(operation):
            yield result

    def query(self, operation: Operation, **kwargs):
        return self.first_link.query(operation, **kwargs)

    def subscribe(self, operation: Operation, **kwargs):
        return self.first_link.subscribe(operation, **kwargs)


def compose(*links: List[Link]) -> ComposedLink:
    """
    Composes a list of Links into a single Link.
    """

    return ComposedLink(links)
