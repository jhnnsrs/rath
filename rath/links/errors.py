from typing import Any
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


def is_auth_error(errors: "list[dict[str, Any]]", codes: "list[str]") -> bool:
    """Whether a GraphQL ``errors`` array is really an authentication failure.

    Servers are free to answer an expired token with ``200 OK`` and an error in the
    body rather than a ``401``/``403`` — that is what a GraphQL error *is*, and it is
    what arkitekt's services do::

        {"errors": [{"message": "...",
                     "extensions": {"code": "UNAUTHENTICATED",
                                    "reason": "TOKEN_EXPIRED"}}]}

    Read as an ordinary ``GraphQLException`` that never reaches
    :class:`~rath.links.auth.AuthTokenLink`, so the token is never refreshed and every
    later operation fails the same way for as long as the process lives.

    Matched on ``code`` alone. ``reason`` names the specific failure and exists so new
    ones can be added without breaking clients, so switching on it would be the
    fragile choice. ``PERMISSION_DENIED`` is deliberately not in the default set: a
    missing scope is not fixed by a new token, and treating it as one buys a refresh
    loop that ends at ``maximum_refresh_attempts``.
    """
    for error in errors:
        if not isinstance(error, dict):
            continue
        extensions = error.get("extensions")
        if isinstance(extensions, dict) and extensions.get("code") in codes:
            return True
    return False
