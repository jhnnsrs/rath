class LinkError(Exception):
    """Base class for all transport errors."""

    pass


class TerminatingLinkError(LinkError):
    """Raised when a terminating link is called."""

    pass


class ContinuationLinkError(LinkError):
    pass


class AuthenticationError(TerminatingLinkError):
    pass
