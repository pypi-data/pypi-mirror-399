"""Token persistence to ~/.datex/credentials.yaml."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from dxs.utils.paths import ensure_secure_permissions, get_credentials_path


class CachedToken(BaseModel):
    """Persisted token data."""

    access_token: str
    refresh_token: str | None = None
    id_token: str | None = None
    token_type: str = "Bearer"
    expires_at: datetime
    scope: list[str] = Field(default_factory=list)
    account_id: str | None = None
    account_username: str | None = None


class TokenCache:
    """Manages token persistence to disk.

    Tokens are stored in ~/.datex/credentials.yaml with secure permissions
    (owner read/write only).
    """

    def __init__(self, path: Path | None = None) -> None:
        """Initialize the token cache.

        Args:
            path: Custom path for credentials file. Defaults to ~/.datex/credentials.yaml.
        """
        self._path = path or get_credentials_path()

    def save_token(self, token_response: dict[str, Any]) -> CachedToken:
        """Save a token response to disk.

        Args:
            token_response: Token response from MSAL.

        Returns:
            The cached token object.
        """
        # Calculate expiration time
        expires_in = token_response.get("expires_in", 3600)
        expires_at = datetime.now(timezone.utc).timestamp() + expires_in

        # Extract account info if available
        account_id = None
        account_username = None
        if "id_token_claims" in token_response:
            claims = token_response["id_token_claims"]
            account_id = claims.get("oid") or claims.get("sub")
            account_username = claims.get("preferred_username") or claims.get("email")

        # Parse scope
        scope_str = token_response.get("scope", "")
        if isinstance(scope_str, str):
            scope = scope_str.split() if scope_str else []
        else:
            scope = scope_str or []

        cached = CachedToken(
            access_token=token_response["access_token"],
            refresh_token=token_response.get("refresh_token"),
            id_token=token_response.get("id_token"),
            token_type=token_response.get("token_type", "Bearer"),
            expires_at=datetime.fromtimestamp(expires_at, timezone.utc),
            scope=scope,
            account_id=account_id,
            account_username=account_username,
        )

        self._write_cache(cached)
        return cached

    def get_token(self) -> CachedToken | None:
        """Get the cached token.

        Returns:
            Cached token if exists, None otherwise.
        """
        return self._read_cache()

    def get_valid_token(self) -> str | None:
        """Get the access token if it exists and is not expired.

        Returns:
            Access token string if valid, None otherwise.
        """
        cached = self._read_cache()
        if cached is None:
            return None

        # Check if expired (with 5-minute buffer)
        now = datetime.now(timezone.utc)
        buffer_seconds = 300  # 5 minutes
        if cached.expires_at.timestamp() <= now.timestamp() + buffer_seconds:
            return None  # Token is expired or about to expire

        return cached.access_token

    def is_expired(self) -> bool:
        """Check if the cached token is expired.

        Returns:
            True if expired or no token cached.
        """
        cached = self._read_cache()
        if cached is None:
            return True

        now = datetime.now(timezone.utc)
        buffer_seconds = 300  # 5 minutes
        return cached.expires_at.timestamp() <= now.timestamp() + buffer_seconds

    def get_expiration(self) -> datetime | None:
        """Get the token expiration time.

        Returns:
            Expiration datetime or None if no token cached.
        """
        cached = self._read_cache()
        return cached.expires_at if cached else None

    def get_account_info(self) -> dict[str, str | None] | None:
        """Get cached account information.

        Returns:
            Dict with account_id and account_username, or None.
        """
        cached = self._read_cache()
        if cached is None:
            return None

        return {
            "account_id": cached.account_id,
            "account_username": cached.account_username,
        }

    def clear(self) -> bool:
        """Remove cached credentials.

        Returns:
            True if credentials were removed, False if none existed.
        """
        if self._path.exists():
            self._path.unlink()
            return True
        return False

    def try_refresh(self) -> str | None:
        """Attempt to refresh the token using stored refresh token.

        Returns:
            New access token if refresh succeeded, None otherwise.
        """
        cached = self._read_cache()
        if cached is None or not cached.refresh_token:
            return None

        try:
            # Import here to avoid circular imports
            from dxs.core.auth.msal_client import MSALClient

            client = MSALClient()
            result = client.refresh_access_token(cached.refresh_token)
            if result:
                new_cached = self.save_token(result)
                return new_cached.access_token
        except Exception:
            pass

        return None

    def _write_cache(self, cached: CachedToken) -> None:
        """Write the cache to disk."""
        # Ensure parent directory exists
        self._path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict for YAML serialization
        data = cached.model_dump(mode="json")

        # Convert datetime to ISO string
        if isinstance(data.get("expires_at"), str):
            pass  # Already a string from mode="json"
        elif data.get("expires_at"):
            data["expires_at"] = data["expires_at"].isoformat()

        # Write with secure permissions
        self._path.write_text(yaml.safe_dump(data, default_flow_style=False))
        ensure_secure_permissions(self._path)

    def _read_cache(self) -> CachedToken | None:
        """Read the cache from disk."""
        if not self._path.exists():
            return None

        try:
            data = yaml.safe_load(self._path.read_text())
            if not data:
                return None

            # Parse datetime string back to datetime
            if isinstance(data.get("expires_at"), str):
                data["expires_at"] = datetime.fromisoformat(data["expires_at"])

            return CachedToken.model_validate(data)
        except (yaml.YAMLError, ValueError, KeyError):
            return None
