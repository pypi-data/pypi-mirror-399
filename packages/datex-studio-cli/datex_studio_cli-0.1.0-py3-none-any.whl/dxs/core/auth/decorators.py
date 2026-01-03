"""Authentication decorators for CLI commands."""

import functools
from typing import Any, Callable, TypeVar

import click

from dxs.core.auth.token_cache import TokenCache
from dxs.utils.errors import AuthenticationError

F = TypeVar("F", bound=Callable[..., Any])


def require_auth(f: F) -> F:
    """Decorator that ensures valid authentication before command execution.

    Checks for a valid, non-expired token in the cache. If expired, attempts
    to refresh using the stored refresh token. If no valid token exists,
    raises an AuthenticationError with instructions to run 'dxs auth login'.

    Usage:
        @source.command()
        @pass_context
        @require_auth
        def my_command(ctx: DxsContext) -> None:
            ...
    """

    @functools.wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        cache = TokenCache()
        token = cache.get_valid_token()

        if token is None:
            # Token expired or missing - try to refresh
            refreshed_token = cache.try_refresh()
            if refreshed_token is not None:
                # Refresh succeeded, continue
                return f(*args, **kwargs)

            # Refresh failed - raise appropriate error
            cached = cache.get_token()
            if cached is not None:
                raise AuthenticationError(
                    message="Authentication token expired and refresh failed",
                    code="DXS-AUTH-001",
                    details={"expired_at": cached.expires_at.isoformat()},
                    suggestions=[
                        "Run 'dxs auth login' to re-authenticate",
                    ],
                )
            else:
                raise AuthenticationError(
                    message="Not authenticated. Please log in first.",
                    code="DXS-AUTH-002",
                    suggestions=[
                        "Run 'dxs auth login' to authenticate",
                        "Use 'dxs auth status' to check authentication state",
                    ],
                )

        return f(*args, **kwargs)

    return wrapper  # type: ignore[return-value]


def get_access_token() -> str:
    """Get the current access token.

    If the token is expired, attempts to refresh it using the stored
    refresh token before failing.

    Returns:
        The access token string.

    Raises:
        AuthenticationError: If not authenticated or token expired and refresh failed.
    """
    cache = TokenCache()
    token = cache.get_valid_token()

    if token is not None:
        return token

    # Token expired or missing - try to refresh
    refreshed_token = cache.try_refresh()
    if refreshed_token is not None:
        return refreshed_token

    # Refresh failed - raise appropriate error
    cached = cache.get_token()
    if cached is not None:
        raise AuthenticationError(
            message="Authentication token expired and refresh failed",
            code="DXS-AUTH-001",
            suggestions=["Run 'dxs auth login' to re-authenticate"],
        )
    else:
        raise AuthenticationError(
            message="Not authenticated. Please log in first.",
            code="DXS-AUTH-002",
            suggestions=["Run 'dxs auth login' to authenticate"],
        )

    return token
