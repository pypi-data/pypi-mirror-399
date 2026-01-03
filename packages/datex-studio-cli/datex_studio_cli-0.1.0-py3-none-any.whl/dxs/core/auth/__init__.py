"""Authentication module for Azure Entra integration."""

from dxs.core.auth.decorators import get_access_token, require_auth
from dxs.core.auth.msal_client import MSALClient
from dxs.core.auth.token_cache import CachedToken, TokenCache

__all__ = [
    "MSALClient",
    "TokenCache",
    "CachedToken",
    "require_auth",
    "get_access_token",
]
