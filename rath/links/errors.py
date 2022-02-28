class LinkError(Exception):
    """Base class for all transport errors."""

    pass


class LinkNotConnectedError(Exception):
    pass

    def __init__(self, message) -> None:
        super().__init__(
            message
            + "\n To connect link please use either an async or sync context manager "
        )


class TerminatingLinkError(LinkError):
    """Raised when a terminating link is called."""

    pass


class ContinuationLinkError(LinkError):
    pass


class AuthenticationError(TerminatingLinkError):
    pass
