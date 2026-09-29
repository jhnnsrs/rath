"""Shared websocket connect helper for the websocket terminating links.

Uses the asyncio client of ``websockets`` (>= 13, ``proxy=`` needs >= 15) and
falls back to the legacy client on older installs, where proxies are not
supported.
"""

import inspect
from ssl import SSLContext
from typing import Any, Dict, List, Optional

try:
    from websockets.asyncio.client import connect as _connect

    LEGACY_WEBSOCKETS = False
except ImportError:  # pragma: no cover - websockets < 13
    from websockets import connect as _connect  # type: ignore

    LEGACY_WEBSOCKETS = True

SUPPORTS_PROXY = not LEGACY_WEBSOCKETS and "proxy" in inspect.signature(_connect).parameters


def ws_connect(
    url: str,
    subprotocols: List[str],
    ssl: Optional[SSLContext],
    proxy: Optional[str] = None,
) -> Any:
    """Open a websocket connection (use as an async context manager).

    Parameters
    ----------
    url : str
        The ws:// or wss:// url to connect to
    subprotocols : List[str]
        The subprotocols to negotiate
    ssl : Optional[SSLContext]
        The ssl context to use for wss:// urls (None for ws://)
    proxy : Optional[str]
        An HTTP proxy url (e.g. ``http://127.0.0.1:41234``) to tunnel the
        connection through via CONNECT. When None, the connection is direct,
        as it always was: websockets >= 15 would otherwise pick a proxy up
        from ``HTTP_PROXY``/``ALL_PROXY``, and fail outright on a SOCKS one
        without python-socks installed.

    Returns
    -------
    Any
        The websockets connect context manager
    """
    kwargs: Dict[str, Any] = {"subprotocols": subprotocols, "ssl": ssl}
    if proxy is not None and not SUPPORTS_PROXY:
        raise RuntimeError(
            "Connecting a websocket through a proxy requires websockets>=15, "
            "but an older version without proxy support is installed."
        )
    if SUPPORTS_PROXY:
        kwargs["proxy"] = proxy
    return _connect(url, **kwargs)  # type: ignore
