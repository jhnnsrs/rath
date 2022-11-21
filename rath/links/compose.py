from typing import List

from pydantic import validator, root_validator
from rath.links.base import ContinuationLink, Link, TerminatingLink
from rath.operation import Operation


class ComposedLink(TerminatingLink):
    """A composed link is a link that is composed of multiple links. The links
    are executed in the order they are passed to the constructor.

    The first link in the chain is the first link that is executed. The last
    link in the chain is the terminating link, which is responsible for sending
    the operation to the server.
    """
    links: List[Link]
    """The links that are composed to form the chain. pydantic will validate that the last link is a terminating link."""

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

        # We need to make sure that the links are connected in the correct order
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
    """A typed composed link is a base class to create a definition for
    a composed link. It is a link that is composed of multiple links that
    will be set at compile time and not at runtime. Just add links
    that you want to use to the class definition and they will be
    automatically composed together.
    """
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
    """Compose a chain of links together. The first link in the chain is the first link that is executed.
    The last link in the chain is the terminating link, which is responsible for sending the operation to the server.


    Returns:
        ComposedLink: The composed link
    """   

    return ComposedLink(links=links)
