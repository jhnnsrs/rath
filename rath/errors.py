class RathException(Exception):
    """RathException is the base exception for all Rath errors."""

    pass


class EntityNotFound(RathException, LookupError):
    """Raised when an entity asked for by id does not exist, or is not one the
    caller may see. A server does not tell the two apart, on purpose."""

    pass


class NotConnectedError(RathException):
    """NotConnectedError is raised when the Rath is not connected and autoload
    is set to false."""

    pass


class NotEnteredError(RathException):
    """NotEnteredError is raised when the Rath is not entered and access
    to protected methods is attempted."""

    pass


class NotComposedError(RathException):
    """NotComposedError is raised when the Rath link chain is not composed and
    the next link is accessed."""

    pass
