class TransportError(Exception):
    """Base class for all transport errors."""

    pass


class AuthenticationError(TransportError):
    pass
