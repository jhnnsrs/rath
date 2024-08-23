""" Links module. 


The links module contains all the links that can be used to compose a client.
A link is a class that implements the Link interface. The Link interface is defined
in the base module. This module also contains some helper functions that can be used
to compose and combine links, to create more complex client behaviour.

"""

from .compose import compose
from .split import split

__all__ = ["compose", "split"]
