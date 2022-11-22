from rath.errors import RathException


class LinkError(RathException):
    """Base class for all link errors."""



class LinkNotConnectedError(LinkError):
    """LinkNotConnectedError is raised when the link is not connected and autoload is set to false."""

    pass

    def __init__(self, message) -> None:
        super().__init__(
            message
            + "\n To connect link please use either an async or sync context manager "
        )


class TerminatingLinkError(LinkError):
    """Raised when a terminating link is called."""



class ContinuationLinkError(LinkError):
    pass


class AuthenticationError(TerminatingLinkError):
    pass
