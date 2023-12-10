from rath.errors import RathException


class LinkError(RathException):
    """Base class for all link errors."""


class LinkNotConnectedError(LinkError):
    """LinkNotConnectedError is raised when the link is not connected and autoload is set to false."""

    pass

    def __init__(self, message: str) -> None:
        """_summary_

        Parameters
        ----------
        message : _type_
            The message to raise (will be preprended to the default message)
        """
        super().__init__(
            message
            + "\n To connect link please use either an async or sync context manager "
        )


class TerminatingLinkError(LinkError):
    """Raised when a terminating link is called.

    This is a base class for all terminating link errors."""


class ContinuationLinkError(LinkError):
    """Raised when a continuation link is called an errors.

    THis is a base class for all continuation link errors."""

    pass


class AuthenticationError(TerminatingLinkError):
    """Signals that the authentication failed."""

    pass
