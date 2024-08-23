""" THe Qt Rath package.

This package contains the QtRathQuery class, which is a subclass of RathQuery
that emits Qt signals when the operation is started, errored, cancelled, or
returned.  This allows you to use it in a Qt application without blocking the
main thread. Attention: This is a work in progress, and is not yet ready for
use.

TODO: This should be more straightforward to use.

"""

from .helpers import QtRathQuery

__all__ = ["QtRathQuery"]
