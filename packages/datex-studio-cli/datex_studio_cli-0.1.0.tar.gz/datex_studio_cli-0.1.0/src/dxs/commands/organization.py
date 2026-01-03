"""Organization commands: dxs organization [list|show|mine|search]."""

import click

from dxs.cli import DxsContext, pass_context
from dxs.core.api import ApiClient, OrganizationEndpoints
from dxs.core.auth import require_auth
from dxs.utils.responses import list_response, search_response, single


@click.group()
def organization() -> None:
    """Organization commands.

    Manage and view organizations in Datex Studio.

    \b
    Examples:
        dxs organization list              # List all organizations
        dxs organization mine              # Show your organization
        dxs organization show 1            # Show organization by ID
        dxs organization search "Datex"    # Search by name
    """
    pass


@organization.command("list")
@pass_context
@require_auth
def org_list(ctx: DxsContext) -> None:
    """List all organizations.

    \b
    Example:
        dxs organization list
    """
    client = ApiClient()
    ctx.log("Fetching organizations...")

    orgs = client.get(OrganizationEndpoints.list())

    # Normalize to list if not already
    if not isinstance(orgs, list):
        orgs = [orgs] if orgs else []

    # Use list_response helper
    ctx.output(list_response(items=orgs, semantic_key="organizations"))


@organization.command()
@click.argument("org_id", type=int)
@pass_context
@require_auth
def show(ctx: DxsContext, org_id: int) -> None:
    """Show organization details.

    \b
    Arguments:
        ORG_ID  Organization ID

    \b
    Example:
        dxs organization show 1
    """
    client = ApiClient()
    ctx.log(f"Fetching organization {org_id}...")

    org_data = client.get(OrganizationEndpoints.get(org_id))

    # Use single helper
    ctx.output(single(item=org_data, semantic_key="organization"))


@organization.command()
@pass_context
@require_auth
def mine(ctx: DxsContext) -> None:
    """Show your organization.

    Returns the organization associated with the current user, including
    full details (description, createdDate, modifiedDate, devOpsOrganization).

    \b
    Example:
        dxs organization mine
    """
    client = ApiClient()
    ctx.log("Fetching your organization...")

    # First get the org ID from /organizations/mine
    org_basic = client.get(OrganizationEndpoints.mine())
    org_id = org_basic.get("id")

    if not org_id:
        # Fallback to basic response if no ID
        ctx.output(single(item=org_basic, semantic_key="organization"))
        return

    # Fetch full organization details with all fields
    ctx.log(f"Fetching full details for organization {org_id}...")
    org_data = client.get(OrganizationEndpoints.get(org_id))

    # Use single helper
    ctx.output(single(item=org_data, semantic_key="organization"))


@organization.command()
@click.argument("query")
@pass_context
@require_auth
def search(ctx: DxsContext, query: str) -> None:
    """Search organizations by name or description.

    Performs case-insensitive search on organization names and descriptions.

    \b
    Arguments:
        QUERY  Search term to match against organization names and descriptions

    \b
    Example:
        dxs organization search "Datex"
    """
    client = ApiClient()
    ctx.log(f"Searching organizations for '{query}'...")

    orgs = client.get(OrganizationEndpoints.list())

    # Normalize to list
    if not isinstance(orgs, list):
        orgs = [orgs] if orgs else []

    total_orgs = len(orgs)

    # Filter by name or description (case-insensitive)
    query_lower = query.lower()
    matches = [
        org for org in orgs
        if query_lower in org.get("name", "").lower()
        or query_lower in (org.get("description") or "").lower()
    ]

    # Use search_response helper
    ctx.output(
        search_response(
            items=matches,
            query=query,
            total_count=total_orgs,
            semantic_key="organizations",
        )
    )
