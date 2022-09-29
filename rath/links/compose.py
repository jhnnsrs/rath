from typing import List

from pydantic import validator, root_validator
from rath.links.base import ContinuationLink, Link, TerminatingLink
from rath.operation import Operation


class ComposedLink(TerminatingLink):
    links: List[Link]

    @validator("links")
    def validate(cls, value):
        if not value:
            raise ValueError("ComposedLink requires at least one link")

        if not all(isinstance(link, Link) for link in value):
            raise ValueError("ComposedLink requires all links to be Links")

        assert isinstance(
            value[-1], TerminatingLink
        ), "Last link must be a TerminatingLink"
        for link in value[:-1]:
            assert isinstance(
                link, ContinuationLink
            ), f"All but the last must be ContinuationLinks: check {link}"

        return value

    async def aconnect(self):
        for link in self.links:
            await link.aconnect()

    async def adisconnect(self):
        for link in self.links:
            await link.adisconnect()

    async def __aenter__(self):
        for i in range(len(self.links) - 1):
            self.links[i].set_next(self.links[i + 1])

        for link in self.links:
            await link.__aenter__()

    async def __aexit__(self, *args, **kwargs):
        for link in self.links:
            await link.__aexit__(*args, **kwargs)

    async def aexecute(self, operation: Operation, **kwargs):
        async for result in self.links[0].aexecute(operation):
            yield result


class TypedComposedLink(TerminatingLink):
    _firstlink: Link = None

    async def aconnect(self):
        for key, link in self:
            if isinstance(link, Link):
                await link.aconnect()

    async def adisconnect(self):
        for key, link in self:
            if isinstance(link, Link):
                await link.adisconnect()

    async def __aenter__(self):

        current_link = None

        for key, link in self:
            if isinstance(link, Link):
                if current_link:
                    current_link.set_next(link)
                    await current_link.__aenter__()
                else:
                    self._firstlink = link
                    await self._firstlink.__aenter__()

                current_link = link

        await current_link.__aenter__()

    async def __aexit__(self, *args, **kwargs):
        for key, link in self:
            if isinstance(link, Link):
                await link.__aexit__(*args, **kwargs)

    async def aexecute(self, operation: Operation, **kwargs):

        async for result in self._firstlink.aexecute(operation):
            yield result

    class Config:
        underscore_attrs_are_private = True


def compose(*links: Link) -> ComposedLink:
    """
    Composes a list of Links into a single Link.
    """

    return ComposedLink(links=links)
