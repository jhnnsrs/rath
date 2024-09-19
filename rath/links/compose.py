from typing import AsyncIterator, List, Optional, Type, Any

from pydantic import field_validator
from rath.links.base import ContinuationLink, Link, TerminatingLink
from rath.operation import GraphQLResult, Operation
from rath.errors import NotComposedError


class ComposedLink(TerminatingLink):
    """A composed link is a link that is composed of multiple links. The links
    are executed in the order they are passed to the constructor.

    The first link in the chain is the first link that is executed. The last
    link in the chain is the terminating link, which is responsible for sending
    the operation to the server.
    """

    links: List[Link]
    """The links that are composed to form the chain. pydantic will validate 
    that the last link is a terminating link."""

    @field_validator("links")
    def validate(cls: Type["ComposedLink"], value: Any, info) -> List[Link]:
        """Validate that the links are valid"""
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

    async def aconnect(self, operation: Operation) -> None:
        """Delegate the connect to all the links"""
        for link in self.links:
            await link.aconnect(operation)

    async def adisconnect(self) -> None:
        """Delegate the disconnect to all the links"""
        for link in self.links:
            await link.adisconnect()

    async def __aenter__(self) -> None:
        """Compose the links together and set the first link as the first link"""
        # We need to make sure that the links are connected in the correct order
        for i in range(len(self.links) - 1):
            self.links[i].set_next(self.links[i + 1])

        for link in self.links:
            await link.__aenter__()

    async def __aexit__(self, *args, **kwargs) -> None:
        """Exit the links in reverse order"""
        for link in self.links:
            await link.__aexit__(*args, **kwargs)

    async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
        """Execute the first link

        This is the main method of the link. It takes an operation and returns an AsyncIterator
        of GraphQLResults. This method should be implemented by subclasses. It is important
        """
        async for result in self.links[0].aexecute(operation):
            yield result


class TypedComposedLink(TerminatingLink):
    """A typed composed link is a base class to create a definition for
    a composed link. It is a link that is composed of multiple links that
    will be set at compile time and not at runtime. Just add links
    that you want to use to the class definition and they will be
    automatically composed together.
    """

    _firstlink: Optional[Link] = None

    async def __aenter__(self) -> None:
        """Compose the links together and set the first link as the first link"""

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

        if current_link:
            await current_link.__aenter__()
        else:
            raise NotComposedError("No links set")

    async def __aexit__(self, *args, **kwargs) -> None:
        """Exit the links in reverse order"""
        for key, link in self:
            if isinstance(link, Link):
                await link.__aexit__(*args, **kwargs)

    async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
        """Execute the first link"""
        if not self._firstlink:
            raise NotComposedError(
                "Links need to be composed before they can be executed. (Through __aenter__)"
            )

        async for result in self._firstlink.aexecute(operation):
            yield result



def compose(*links: Link) -> ComposedLink:
    """Compose a chain of links together. The first link in the chain is the first link that is executed.
    The last link in the chain is the terminating link, which is responsible for sending the operation to the server.


    Returns:
        ComposedLink: The composed link
    """

    return ComposedLink(links=links)
