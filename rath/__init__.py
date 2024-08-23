"""Rath

Rath is a GraphQL client for Python that is designed to be easy to use and
extendable. It follows the GraphQL spec and supports queries, mutations, and
subscriptions, with a focus on enabling apollo client like features in Python.

It can interface with a variety of transports and is designed to be easy to
extend and add new features to, thorugh the composition of links.

Rath is built on top of [pydantic](https://pydantic-docs.helpmanual.io/).

"""

from .rath import Rath

__all__ = ["Rath"]
