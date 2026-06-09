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


class TokenLoaderNotSetError(ContinuationLinkError):
    """Raised when an auth link needs to load a token but no token_loader is configured.

    Either pass a ``token_loader`` to ``ComposedAuthLink`` or subclass ``AuthTokenLink``
    and override ``aload_token``."""

    pass


class TokenRefresherNotSetError(ContinuationLinkError):
    """Raised when an auth link needs to refresh an expired token but no token_refresher is configured.

    Either pass a ``token_refresher`` to ``ComposedAuthLink`` or subclass ``AuthTokenLink``
    and override ``arefresh_token``."""

    pass


class MalformedResponseError(TerminatingLinkError):
    """Raised when the server returns a 200 response that contains neither ``data`` nor ``errors``.

    This usually indicates that the endpoint is not a GraphQL endpoint, or that a
    proxy/load-balancer returned an unexpected body."""

    pass
