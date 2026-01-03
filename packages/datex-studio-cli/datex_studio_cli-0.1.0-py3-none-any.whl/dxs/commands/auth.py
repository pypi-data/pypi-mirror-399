"""Authentication commands: dxs auth [login|logout|status]."""

from datetime import datetime, timedelta, timezone
from typing import Any

import click

from dxs.cli import DxsContext, pass_context
from dxs.core.auth import MSALClient, TokenCache
from dxs.utils.errors import AuthenticationError
from dxs.utils.responses import single


@click.group()
def auth() -> None:
    """Authentication commands.

    Manage authentication with Azure Entra (Azure AD) using device code flow.
    Tokens are stored in ~/.datex/credentials.yaml.

    \b
    The device code flow works as follows:
    1. Run 'dxs auth login'
    2. A code and URL will be displayed
    3. Open the URL in a browser and enter the code
    4. Complete authentication in the browser
    5. The CLI will automatically receive the token
    """
    pass


@auth.command()
@pass_context
def login(ctx: DxsContext) -> None:
    """Authenticate with Azure Entra using device code flow.

    Uses device code flow for authentication. On first login, you may need
    to complete multiple authentication prompts to consent to all required
    API permissions. Subsequent logins will only require a single prompt.

    \b
    Example:
        dxs auth login
    """
    from dxs.utils.config import get_settings

    cache = TokenCache()

    # Check if already authenticated with valid token
    existing_token = cache.get_valid_token()
    if existing_token:
        account_info = cache.get_account_info()
        ctx.output(
            single(
                item={
                    "status": "already_authenticated",
                    "message": "You are already logged in",
                    "account": account_info.get("account_username") if account_info else None,
                    "hint": "Use 'dxs auth logout' to sign out first",
                },
                semantic_key="authentication",
            )
        )
        return

    settings = get_settings()

    try:
        client = MSALClient(scopes=settings.azure_scopes)
    except AuthenticationError as e:
        ctx.output_error(e)
        raise SystemExit(1)

    def on_device_code(device_code: dict[str, Any]) -> None:
        """Callback to display device code to user."""
        ctx.output(
            single(
                item={
                    "status": "awaiting_authentication",
                    "action_required": {
                        "type": "device_code",
                        "instructions": "Open the URL in a browser and enter the code to authenticate",
                        "url": device_code["verification_uri"],
                        "code": device_code["user_code"],
                        "expires_in_seconds": device_code["expires_in"],
                    },
                    "message": device_code.get("message", ""),
                },
                semantic_key="authentication",
            ),
            include_metadata=False,
        )

    def on_additional_consent_needed(resource_name: str, scopes: list[str]) -> None:
        """Callback when additional consent is needed for a resource."""
        ctx.log(f"Additional consent needed for: {resource_name}")
        ctx.output(
            single(
                item={
                    "status": "additional_consent_needed",
                    "message": f"Additional consent required for {resource_name}",
                    "resource": resource_name,
                    "scopes": scopes,
                },
                semantic_key="authentication",
            ),
            include_metadata=False,
        )

    try:
        ctx.log("Initiating device code authentication...")

        # Build additional scope sets, filtering out empty ones
        # (e.g., dynamics_crm_scopes is empty if dynamics_crm_url is not configured)
        additional_scope_sets = [
            scopes for scopes in [
                settings.azure_devops_scopes,
                settings.dynamics_crm_scopes,
            ] if scopes  # Filter out empty scope lists
        ]

        result = client.authenticate_device_code_multi_resource(
            primary_scopes=settings.azure_scopes,
            additional_scope_sets=additional_scope_sets,
            on_device_code=on_device_code,
            on_additional_consent_needed=on_additional_consent_needed,
        )

        # Save token to cache
        cached = cache.save_token(result)

        # Output success
        ctx.output(
            single(
                item={
                    "status": "authenticated",
                    "message": "Successfully authenticated",
                    "account": cached.account_username,
                    "expires_at": cached.expires_at.isoformat(),
                },
                semantic_key="authentication",
            )
        )

    except AuthenticationError as e:
        ctx.output_error(e)
        raise SystemExit(1)


@auth.command()
@pass_context
def logout(ctx: DxsContext) -> None:
    """Clear stored credentials.

    Removes the cached authentication token from ~/.datex/credentials.yaml.

    \b
    Example:
        dxs auth logout
    """
    cache = TokenCache()

    # Get account info before clearing
    account_info = cache.get_account_info()
    account_name = account_info.get("account_username") if account_info else None

    # Clear the cache
    was_logged_in = cache.clear()

    if was_logged_in:
        ctx.output(
            single(
                item={
                    "status": "logged_out",
                    "message": "Successfully logged out",
                    "account": account_name,
                },
                semantic_key="authentication",
            )
        )
    else:
        ctx.output(
            single(
                item={
                    "status": "not_logged_in",
                    "message": "No credentials to clear - you were not logged in",
                },
                semantic_key="authentication",
            )
        )


@auth.command()
@pass_context
def status(ctx: DxsContext) -> None:
    """Show current authentication status.

    Displays whether you are authenticated and token expiration info for all resources.

    \b
    Example:
        dxs auth status
    """
    from dxs.utils.config import get_settings

    cache = TokenCache()
    cached = cache.get_token()

    if cached is None:
        ctx.output(
            single(
                item={
                    "authenticated": False,
                    "status": "not_authenticated",
                    "message": "Not logged in",
                    "suggestion": "Run 'dxs auth login' to authenticate",
                },
                semantic_key="authentication",
            )
        )
        return

    # Check primary token expiration
    now = datetime.now(timezone.utc)
    is_expired = cached.expires_at <= now
    expires_in_seconds = int((cached.expires_at - now).total_seconds())

    # If primary token is expired, try to refresh it before reporting as expired
    if is_expired:
        ctx.log("Primary access token is expired, attempting to refresh...")

        if cached.refresh_token:
            try:
                # Try to refresh the primary token
                settings = get_settings()
                client = MSALClient()
                refresh_result = client._app.acquire_token_by_refresh_token(
                    refresh_token=cached.refresh_token,
                    scopes=settings.azure_scopes,
                )

                if refresh_result and "access_token" in refresh_result:
                    # Refresh succeeded! Update the cache
                    ctx.log("Successfully refreshed access token")
                    refreshed_token = cache.save_token(refresh_result)

                    # Update our variables with the new token
                    cached = refreshed_token
                    is_expired = False
                    expires_in_seconds = int((cached.expires_at - now).total_seconds())
                else:
                    # Refresh failed - extract error details
                    error = refresh_result.get("error") if refresh_result else "unknown"
                    error_desc = refresh_result.get("error_description", "") if refresh_result else ""

                    ctx.output(
                        single(
                            item={
                                "authenticated": False,
                                "status": "refresh_token_expired",
                                "message": "Authentication token has expired and refresh token is no longer valid",
                                "account": cached.account_username,
                                "expired_at": cached.expires_at.isoformat(),
                                "refresh_error": error,
                                "refresh_error_description": error_desc if error_desc else None,
                                "suggestion": "Run 'dxs auth login' to authenticate again",
                            },
                            semantic_key="authentication",
                        )
                    )
                    return
            except Exception as e:
                # Refresh attempt failed with exception
                ctx.output(
                    single(
                        item={
                            "authenticated": False,
                            "status": "refresh_failed",
                            "message": "Authentication token has expired and refresh attempt failed",
                            "account": cached.account_username,
                            "expired_at": cached.expires_at.isoformat(),
                            "refresh_error": str(e),
                            "suggestion": "Run 'dxs auth login' to authenticate again",
                        },
                        semantic_key="authentication",
                    )
                )
                return
        else:
            # No refresh token available
            ctx.output(
                single(
                    item={
                        "authenticated": False,
                        "status": "token_expired",
                        "message": "Authentication token has expired and no refresh token available",
                        "account": cached.account_username,
                        "expired_at": cached.expires_at.isoformat(),
                        "suggestion": "Run 'dxs auth login' to refresh credentials",
                    },
                    semantic_key="authentication",
                )
            )
            return

    # Calculate human-readable expiration
    def format_expiration(seconds: int) -> str:
        if seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            return f"{seconds // 60} minutes"
        else:
            return f"{seconds // 3600} hours"

    # Check all cached tokens
    settings = get_settings()
    client = MSALClient()

    # Define resources to check (only include resources with configured scopes)
    resources = {
        "datex_api": {
            "name": "Datex Studio API",
            "scopes": settings.azure_scopes,
        },
        "azure_devops": {
            "name": "Azure DevOps API",
            "scopes": settings.azure_devops_scopes,
        },
    }

    # Only include Dynamics CRM if URL is configured
    if settings.dynamics_crm_scopes:
        resources["dynamics_crm"] = {
            "name": "Dynamics CRM API",
            "scopes": settings.dynamics_crm_scopes,
        }

    tokens_info = []
    refresh_token_expired = False
    refresh_token_error_details = None

    for resource_key, resource_info in resources.items():
        try:
            # Try to acquire token using refresh token from cache
            if cached.refresh_token:
                result = client._app.acquire_token_by_refresh_token(
                    refresh_token=cached.refresh_token,
                    scopes=resource_info["scopes"],
                )
                if result and "access_token" in result:
                    # expires_in is seconds from now, not a timestamp
                    expires_in_from_response = result.get("expires_in", 3600)
                    expires_at = now + timedelta(seconds=expires_in_from_response)
                    token_expires_in = expires_in_from_response

                    tokens_info.append({
                        "resource": resource_info["name"],
                        "scopes": resource_info["scopes"],
                        "has_token": True,
                        "expires_at": expires_at.isoformat(),
                        "expires_in_seconds": token_expires_in,
                        "expires_in_human": format_expiration(token_expires_in),
                    })
                else:
                    # Check for error details
                    error = result.get("error") if result else "no_token"
                    error_description = result.get("error_description", "") if result else ""

                    # Detect if refresh token is expired
                    if error == "invalid_grant" or "refresh token" in error_description.lower() and "expired" in error_description.lower():
                        refresh_token_expired = True
                        refresh_token_error_details = {
                            "error": error,
                            "description": error_description,
                        }

                    tokens_info.append({
                        "resource": resource_info["name"],
                        "scopes": resource_info["scopes"],
                        "has_token": False,
                        "error": error,
                        "error_description": error_description if error_description else None,
                    })
            else:
                tokens_info.append({
                    "resource": resource_info["name"],
                    "scopes": resource_info["scopes"],
                    "has_token": False,
                    "error": "no_refresh_token",
                })
        except Exception as e:
            tokens_info.append({
                "resource": resource_info["name"],
                "scopes": resource_info["scopes"],
                "has_token": False,
                "error": str(e),
            })

    # Build the status item
    status_item = {
        "authenticated": True,
        "status": "authenticated",
        "message": "You are logged in",
        "account": cached.account_username,
        "primary_token": {
            "expires_at": cached.expires_at.isoformat(),
            "expires_in_seconds": expires_in_seconds,
            "expires_in_human": format_expiration(expires_in_seconds),
        },
        "tokens": tokens_info,
    }

    # Add refresh token status
    if refresh_token_expired:
        status_item["refresh_token_status"] = "expired"
        status_item["refresh_token_error"] = refresh_token_error_details
        status_item["warning"] = "Your refresh token has expired. Some API resources may be inaccessible. Run 'dxs auth login' to refresh credentials."
    elif cached.refresh_token:
        status_item["refresh_token_status"] = "valid"
    else:
        status_item["refresh_token_status"] = "missing"
        status_item["warning"] = "No refresh token available. Run 'dxs auth login' to obtain one."

    ctx.output(
        single(
            item=status_item,
            semantic_key="authentication",
        )
    )


