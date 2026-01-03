"""Branch commands: dxs branch [list|show|roles|shell|validate|candelete|search]."""

from datetime import datetime
from typing import Any

import click

from dxs.cli import DxsContext, pass_context
from concurrent.futures import ThreadPoolExecutor, as_completed

from dxs.core.api import ApiClient, BranchEndpoints, RepoEndpoints, SourceControlEndpoints
from dxs.core.api.models import (
    BRANCH_STATUS_ALIASES,
    BRANCH_STATUS_CONTEXT,
    BRANCH_STATUS_NAMES,
    BranchStatus,
)
from dxs.core.auth import require_auth
from dxs.utils import (
    BRANCH_SORT_FIELDS,
    EntityResolver,
    ListFilter,
    author_filter_option,
    date_range_options,
    get_mapped_sort_field,
    pagination_options,
    sort_items,
    sorting_options,
)
from dxs.utils.errors import ValidationError
from dxs.utils.responses import list_response, search_response, single


def enrich_branch_with_status(branch: dict[str, Any]) -> dict[str, Any]:
    """Add human-readable status info to branch data for LLM consumption.

    Enriches a branch dictionary with:
    - statusName: Human-readable status (e.g., "Draft", "WorkspaceActive")
    - statusContext: Semantic description for LLM understanding
    - isCommit: True if this is a commit snapshot (WorkspaceHistory)
    - isRelease: True if this is a published release (Active or Inactive)
    - isCurrentRelease: True if this is the current release (Active)
    - isFeatureBranch: True if this is a feature branch (WorkspaceActive)
    - isMainBranch: True if this is the main branch (Draft)

    Args:
        branch: Branch data dictionary from the API

    Returns:
        Enriched branch dictionary with status information
    """
    status_id = branch.get("applicationStatusId")
    branch["statusName"] = BRANCH_STATUS_NAMES.get(status_id, "Unknown")
    branch["statusContext"] = BRANCH_STATUS_CONTEXT.get(status_id, "")

    # Add semantic flags for easy LLM filtering/understanding
    branch["isCommit"] = status_id == BranchStatus.WORKSPACE_HISTORY
    branch["isRelease"] = status_id in (BranchStatus.ACTIVE, BranchStatus.INACTIVE)
    branch["isCurrentRelease"] = status_id == BranchStatus.ACTIVE
    branch["isFeatureBranch"] = status_id == BranchStatus.WORKSPACE_ACTIVE
    branch["isMainBranch"] = status_id == BranchStatus.DRAFT

    return branch


def _fetch_branch_changes(
    client: ApiClient,
    branch_id: int,
    status_id: int,
) -> tuple[int, dict[str, int] | None]:
    """Fetch change counts for a single branch.

    Args:
        client: API client instance
        branch_id: Branch ID to fetch changes for
        status_id: Branch status ID (determines which endpoint to use)

    Returns:
        Tuple of (branch_id, change_counts dict or None if not applicable/failed)
        change_counts contains: total, created, updated, deleted
    """
    try:
        # Only fetch changes for feature (5) and history (4) branches
        if status_id == BranchStatus.WORKSPACE_ACTIVE:
            data = client.get(SourceControlEndpoints.feature_branch_changes(branch_id))
        elif status_id == BranchStatus.WORKSPACE_HISTORY:
            data = client.get(SourceControlEndpoints.history_branch_changes(branch_id))
        else:
            return branch_id, None

        configs = data.get("configs", [])
        return branch_id, {
            "total": len(configs),
            "created": sum(
                1 for c in configs if c.get("modificationTypeId", "").lower() in ("add", "created")
            ),
            "updated": sum(
                1 for c in configs if c.get("modificationTypeId", "").lower() in ("update", "updated")
            ),
            "deleted": sum(
                1 for c in configs if c.get("modificationTypeId", "").lower() in ("delete", "deleted")
            ),
        }
    except Exception:
        return branch_id, None


def _fetch_changes_parallel(
    client: ApiClient,
    branches: list[dict[str, Any]],
    max_workers: int = 15,
    progress_callback: Any | None = None,
) -> dict[int, dict[str, int]]:
    """Fetch change counts for multiple branches in parallel.

    Args:
        client: API client instance
        branches: List of branch dictionaries with 'id' and 'applicationStatusId'
        max_workers: Maximum concurrent requests
        progress_callback: Optional callback(completed, total) for progress updates

    Returns:
        Dictionary mapping branch_id to change_counts dict
    """
    results: dict[int, dict[str, int]] = {}
    total = len(branches)
    completed = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                _fetch_branch_changes,
                client,
                b["id"],
                b.get("applicationStatusId", 0),
            ): b["id"]
            for b in branches
        }

        for future in as_completed(futures):
            branch_id, counts = future.result()
            if counts is not None:
                results[branch_id] = counts
            completed += 1
            if progress_callback:
                progress_callback(completed, total)

    return results


@click.group()
def branch() -> None:
    """Branch commands.

    Manage and view branches (working copies) in Datex Studio.
    A branch represents a version of a repository that can be
    developed independently.

    \b
    Examples:
        dxs branch list --repo 10       # List branches for repository
        dxs branch show 100             # Show branch details
        dxs branch roles 100            # Show branch roles
        dxs branch shell 100            # Show shell configuration
        dxs branch validate 100         # Validate branch
        dxs branch candelete 100        # Check if deletable
        dxs branch search "Production"  # Search by name
    """
    pass


def _resolve_repo_id(
    ctx: DxsContext,
    repo: int | None,
    repo_name: str | None,
    org: str | None,
    resolver: EntityResolver,
) -> int:
    """Resolve repository ID from various inputs.

    Priority: explicit --repo > --repo-name > context default

    Args:
        ctx: CLI context with default values
        repo: Explicit repository ID
        repo_name: Repository name to resolve
        org: Organization name/ID to scope repo search
        resolver: Entity resolver for name lookup

    Returns:
        Repository ID as integer

    Raises:
        ValidationError: If no repository can be determined
    """
    # Priority: explicit --repo > --repo-name > context
    if repo:
        return repo

    if repo_name:
        org_id = resolver.resolve_org(org) if org else None
        return resolver.resolve_repo(repo_name, org_id)

    if ctx.repo:
        return ctx.repo

    raise ValidationError(
        message="Repository ID required",
        suggestions=[
            "Use --repo flag: dxs source branch list --repo 10",
            "Use --repo-name flag: dxs source branch list --repo-name 'MyApp'",
            "Set environment variable: export DXS_REPO=10",
        ],
    )


@branch.command("list")
@click.option(
    "--repo",
    "-r",
    type=int,
    help="Repository ID",
)
@click.option(
    "--repo-name",
    type=str,
    help="Repository name (resolved to ID)",
)
@click.option(
    "--org",
    type=str,
    help="Organization name or ID (to scope repo search)",
)
@click.option(
    "--all-repos",
    is_flag=True,
    default=False,
    help="Search across all repositories (ignores --repo and --repo-name)",
)
@click.option(
    "--status",
    "status_filter",
    type=click.Choice(
        ["draft", "inactive", "active", "history", "feature", "all"],
        case_sensitive=False,
    ),
    default=None,
    help="Filter by branch status type (draft, inactive, active, history, feature)",
)
@pagination_options(default_limit=10)
@sorting_options(
    sort_choices=["name", "created", "modified", "commit-date", "status", "changes"],
    default_sort="created",
    default_direction="desc",
)
@date_range_options()
@author_filter_option()
@click.option(
    "--with-changes",
    is_flag=True,
    default=False,
    help="Fetch and include change counts for each branch (slower, enables --sort changes)",
)
@pass_context
@require_auth
def branch_list(
    ctx: DxsContext,
    repo: int | None,
    repo_name: str | None,
    org: str | None,
    all_repos: bool,
    status_filter: str | None,
    limit: int,
    sort: str,
    sort_direction: str | None,
    created_after: datetime | None,
    created_before: datetime | None,
    modified_after: datetime | None,
    modified_before: datetime | None,
    author: str | None,
    with_changes: bool,
) -> None:
    """List branches for a repository with filtering and sorting.

    Supports filtering by status, date ranges, author, and sorting by various fields.
    Use --repo or --repo-name to specify the repository, or --all-repos to search
    across all repositories.

    \b
    Status Types:
        draft     Main development branch (receives commits)
        inactive  Previous published releases
        active    Current published release
        history   Commit snapshots (frozen after commit)
        feature   Feature branches (active development)
        all       All branches (default if not specified)

    \b
    Options:
        --repo, -r         Repository ID
        --repo-name        Repository name (resolved to ID)
        --org              Organization to scope repo search
        --all-repos        Search across all repositories
        --status           Filter by status type
        --limit, -n        Maximum results (default: 10, 0 for unlimited)
        --with-changes     Include change counts (enables --sort changes)
        --sort             Sort by: name, created, modified, commit-date, status, changes
        --asc/--desc       Sort direction (default: desc)
        --created-after    Filter by creation date (after)
        --created-before   Filter by creation date (before)
        --modified-after   Filter by modification date (after)
        --modified-before  Filter by modification date (before)
        --author           Filter by author email

    \b
    Examples:
        dxs source branch list --repo 10
        dxs source branch list --repo 10 --status feature
        dxs source branch list --all-repos --status feature --modified-after 2024-01-01
        dxs source branch list --repo 10 --status history --sort commit-date
        dxs source branch list --repo-name "MyApp" --org "Datex"
        dxs source branch list --repo 10 --sort name --asc
        dxs source branch list --repo 10 --created-after 2024-01-01 --limit 5
        dxs source branch list --repo 10 --author "user@example.com"
        dxs source branch list --all-repos --status feature --with-changes --sort changes
    """
    resolver = EntityResolver()
    client = ApiClient()

    # Handle --all-repos mode
    if all_repos:
        ctx.log("Fetching all repositories...")
        repos = client.get(RepoEndpoints.list())
        if not isinstance(repos, list):
            repos = [repos] if repos else []

        ctx.log(f"Fetching branches from {len(repos)} repositories...")
        branches = []
        repos_with_matches = 0

        for repo_data in repos:
            rid = repo_data.get("id")
            rname = repo_data.get("name", f"Repo {rid}")
            try:
                repo_branches = client.get(BranchEndpoints.list(rid))
                if not isinstance(repo_branches, list):
                    repo_branches = [repo_branches] if repo_branches else []

                # Add repo context to each branch
                for b in repo_branches:
                    b["repositoryId"] = rid
                    b["repositoryName"] = rname

                if repo_branches:
                    repos_with_matches += 1
                branches.extend(repo_branches)
            except Exception as e:
                ctx.debug(f"Failed to fetch branches for repo {rid}: {e}")

        total_count = len(branches)
        repo_id = None  # No single repo in all-repos mode
        ctx.log(f"Found {total_count} branches across {repos_with_matches} repositories")
    else:
        # Resolve repo_id from various inputs
        repo_id = _resolve_repo_id(ctx, repo, repo_name, org, resolver)

        ctx.log(f"Fetching branches for repository {repo_id}...")

        # Fetch all branches (API doesn't support server-side filtering)
        branches = client.get(BranchEndpoints.list(repo_id))

        # Normalize to list
        if not isinstance(branches, list):
            branches = [branches] if branches else []

        total_count = len(branches)

    # Apply status filter
    if status_filter and status_filter.lower() != "all":
        status_id = BRANCH_STATUS_ALIASES.get(status_filter.lower())
        if status_id:
            ctx.log(f"Filtering by status: {status_filter} (id={status_id})...")
            branches = [
                b for b in branches if b.get("applicationStatusId") == status_id
            ]

    # Apply author filter (resolve email to userId)
    if author:
        ctx.log(f"Filtering by author: {author}...")
        user_id = resolver.resolve_user_email(author)
        if user_id:
            branches = [b for b in branches if b.get("userId") == user_id]
        else:
            ctx.log(f"Warning: User '{author}' not found, no branches will match")
            branches = []

    # Apply date filters using ListFilter
    branches = (
        ListFilter(branches)
        .by_date_range("createdDate", after=created_after, before=created_before)
        .by_date_range("modifiedDate", after=modified_after, before=modified_before)
        .result()
    )

    filtered_count = len(branches)

    # Validate --sort changes requires --with-changes
    if sort == "changes" and not with_changes:
        raise ValidationError(
            message="--sort changes requires --with-changes flag",
            code="DXS-VAL-002",
            suggestions=[
                "Add --with-changes flag: dxs source branch list --with-changes --sort changes",
                "Use a different sort field: --sort modified",
            ],
        )

    # Fetch change counts if requested (only for feature/history branches)
    if with_changes and branches:
        # Filter to branches that support change counts
        changeable_statuses = {
            BranchStatus.WORKSPACE_ACTIVE,
            BranchStatus.WORKSPACE_HISTORY,
        }
        branches_to_fetch = [
            b for b in branches if b.get("applicationStatusId") in changeable_statuses
        ]

        if branches_to_fetch:
            ctx.log(f"Fetching change counts for {len(branches_to_fetch)} branches...")

            def progress_callback(completed: int, total: int) -> None:
                if completed % 10 == 0 or completed == total:
                    ctx.log(f"  Progress: {completed}/{total} branches...")

            change_counts = _fetch_changes_parallel(
                client, branches_to_fetch, max_workers=15, progress_callback=progress_callback
            )

            # Enrich branches with change data
            for b in branches:
                branch_id = b["id"]
                if branch_id in change_counts:
                    counts = change_counts[branch_id]
                    b["change_count"] = counts["total"]
                    b["changes_summary"] = {
                        "created": counts["created"],
                        "updated": counts["updated"],
                        "deleted": counts["deleted"],
                    }
                else:
                    # Branch doesn't support changes or fetch failed
                    b["change_count"] = None
                    b["changes_summary"] = None

            ctx.log(f"Fetched change counts for {len(change_counts)} branches")

    # Apply sorting
    direction = sort_direction or "desc"
    sort_field = get_mapped_sort_field(sort, BRANCH_SORT_FIELDS)
    branches = sort_items(branches, sort_field, direction)

    # Apply limit (0 means unlimited)
    if limit > 0:
        branches = branches[:limit]

    # Enrich branches with human-readable status info for LLM consumption
    branches = [enrich_branch_with_status(b) for b in branches]

    # Build metadata with all context
    metadata_kwargs = {
        "total_count": total_count,
        "filtered_count": filtered_count,
    }

    # Add repo context (None if all-repos mode)
    if all_repos:
        metadata_kwargs["all_repos"] = True
        metadata_kwargs["repository_count"] = len(repos) if repos else 0
    else:
        metadata_kwargs["repository_id"] = repo_id

    # Add sort info to metadata
    metadata_kwargs["sort_field"] = sort
    metadata_kwargs["sort_direction"] = direction
    metadata_kwargs["limit"] = limit if limit > 0 else None

    # Add applied filters to metadata if any
    if status_filter and status_filter.lower() != "all":
        metadata_kwargs["status_filter"] = status_filter
    if created_after:
        metadata_kwargs["created_after"] = created_after.isoformat()
    if created_before:
        metadata_kwargs["created_before"] = created_before.isoformat()
    if modified_after:
        metadata_kwargs["modified_after"] = modified_after.isoformat()
    if modified_before:
        metadata_kwargs["modified_before"] = modified_before.isoformat()
    if author:
        metadata_kwargs["author_filter"] = author
    if with_changes:
        metadata_kwargs["includes_changes"] = True

    ctx.output(list_response(items=branches, semantic_key="branches", **metadata_kwargs))


@branch.command()
@click.argument("branch_id", type=int)
@pass_context
@require_auth
def show(ctx: DxsContext, branch_id: int) -> None:
    """Show branch details.

    Returns branch information including status context for LLM consumption.

    \b
    Arguments:
        BRANCH_ID  Branch ID

    \b
    Example:
        dxs branch show 100
    """
    client = ApiClient()
    ctx.log(f"Fetching branch {branch_id}...")

    branch_data = client.get(BranchEndpoints.get(branch_id))

    # Enrich with human-readable status info for LLM consumption
    branch_data = enrich_branch_with_status(branch_data)

    ctx.output(single(item=branch_data, semantic_key="branch"))


@branch.command()
@click.argument("branch_id", type=int)
@pass_context
@require_auth
def roles(ctx: DxsContext, branch_id: int) -> None:
    """Show branch roles.

    \b
    Arguments:
        BRANCH_ID  Branch ID

    \b
    Example:
        dxs branch roles 100
    """
    client = ApiClient()
    ctx.log(f"Fetching roles for branch {branch_id}...")

    roles_data = client.get(BranchEndpoints.roles(branch_id))

    # Normalize to list if not already
    if not isinstance(roles_data, list):
        roles_data = [roles_data] if roles_data else []

    ctx.output(list_response(items=roles_data, semantic_key="roles", branch_id=branch_id))


@branch.command()
@click.argument("branch_id", type=int)
@pass_context
@require_auth
def shell(ctx: DxsContext, branch_id: int) -> None:
    """Show branch shell configuration.

    \b
    Arguments:
        BRANCH_ID  Branch ID

    \b
    Example:
        dxs branch shell 100
    """
    client = ApiClient()
    ctx.log(f"Fetching shell configuration for branch {branch_id}...")

    shell_data = client.get(BranchEndpoints.shell(branch_id))

    ctx.output(single(item=shell_data, semantic_key="shell", branch_id=branch_id))


@branch.command()
@click.argument("branch_id", type=int)
@pass_context
@require_auth
def validate(ctx: DxsContext, branch_id: int) -> None:
    """Validate branch configuration.

    Returns a list of validation errors if any exist.

    \b
    Arguments:
        BRANCH_ID  Branch ID

    \b
    Example:
        dxs branch validate 100
    """
    client = ApiClient()
    ctx.log(f"Validating branch {branch_id}...")

    # validate endpoint uses POST
    errors = client.post(BranchEndpoints.validate(branch_id))

    # Normalize to list if not already
    if not isinstance(errors, list):
        errors = [errors] if errors else []

    validation_result = {
        "valid": len(errors) == 0,
        "errors": errors,
    }

    ctx.output(
        single(
            item=validation_result,
            semantic_key="validation",
            branch_id=branch_id,
            error_count=len(errors),
        )
    )


@branch.command()
@click.argument("branch_id", type=int)
@pass_context
@require_auth
def candelete(ctx: DxsContext, branch_id: int) -> None:
    """Check if branch can be deleted.

    Returns whether the branch can be deleted and reasons if not.

    \b
    Arguments:
        BRANCH_ID  Branch ID

    \b
    Example:
        dxs branch candelete 100
    """
    client = ApiClient()
    ctx.log(f"Checking if branch {branch_id} can be deleted...")

    result = client.get(BranchEndpoints.candelete(branch_id))

    ctx.output(single(item=result, semantic_key="canDelete", branch_id=branch_id))


@branch.command()
@click.argument("branch_id", type=int)
@pass_context
@require_auth
def baseline(ctx: DxsContext, branch_id: int) -> None:
    """Find the baseline (previous release) for a branch.

    Returns the most recent Inactive branch from the same repository,
    which represents the previous published version. This is useful for
    generating release notes comparing the new version to the baseline.

    \b
    Arguments:
        BRANCH_ID  Branch ID of the target version

    \b
    Returns:
        The most recent Inactive branch for the same repository

    \b
    Example:
        dxs source branch baseline 63338
        # Returns branch 62582 (the previous published version)
    """
    client = ApiClient()
    ctx.log(f"Finding baseline for branch {branch_id}...")

    # Get the target branch to find its repo ID
    branch_data = client.get(BranchEndpoints.get(branch_id))
    repo_id = branch_data.get("applicationDefinitionId")

    if not repo_id:
        raise ValidationError(
            message=f"Could not determine repository for branch {branch_id}",
            code="DXS-VAL-001",
        )

    ctx.log(f"Fetching inactive branches for repository {repo_id}...")

    # Get all branches for the repo
    branches = client.get(BranchEndpoints.list(repo_id))

    if not isinstance(branches, list):
        branches = [branches] if branches else []

    # Filter to Inactive status only
    inactive_status_id = BRANCH_STATUS_ALIASES.get("inactive")
    inactive_branches = [
        b for b in branches if b.get("applicationStatusId") == inactive_status_id
    ]

    if not inactive_branches:
        ctx.output(
            single(
                item={"message": "No baseline found (no inactive branches)"},
                semantic_key="baseline",
                branch_id=branch_id,
                repository_id=repo_id,
            )
        )
        return

    # Sort by createdDate descending to get the most recent
    inactive_branches = sort_items(inactive_branches, "createdDate", "desc")

    # Get the most recent inactive branch
    baseline_branch = inactive_branches[0]

    # Enrich with status info
    baseline_branch = enrich_branch_with_status(baseline_branch)

    ctx.output(
        single(
            item=baseline_branch,
            semantic_key="baseline",
            target_branch_id=branch_id,
            repository_id=repo_id,
        )
    )


@branch.command()
@click.argument("query")
@click.option(
    "--repo",
    "repo",
    type=int,
    help="Repository ID (overrides context default)",
)
@pass_context
@require_auth
def search(ctx: DxsContext, query: str, repo: int | None) -> None:
    """Search branches by name.

    Performs case-insensitive search on branch names.

    \b
    Arguments:
        QUERY  Search term to match against branch names

    \b
    Options:
        --repo  Repository ID (or set DXS_REPO)

    \b
    Example:
        dxs branch search "Production" --repo 10
    """
    repo_id = repo or ctx.repo
    if not repo_id:
        raise ValidationError(
            message="Repository ID required for search",
            suggestions=[
                "Use --repo flag: dxs branch search 'query' --repo 10",
                "Set environment variable: export DXS_REPO=10",
                "Set config default: dxs config set default_repo 10",
            ],
        )

    client = ApiClient()
    ctx.log(f"Searching branches for '{query}' in repository {repo_id}...")

    branches = client.get(BranchEndpoints.list(repo_id))

    # Normalize to list
    if not isinstance(branches, list):
        branches = [branches] if branches else []

    # Filter by name (case-insensitive)
    query_lower = query.lower()
    matches = [
        b for b in branches
        if query_lower in b.get("name", "").lower()
    ]

    # Enrich with human-readable status info for LLM consumption
    matches = [enrich_branch_with_status(b) for b in matches]

    ctx.output(
        search_response(
            items=matches,
            query=query,
            total_count=len(branches),
            semantic_key="branches",
            repository_id=repo_id,
        )
    )


@branch.command()
@click.argument("branch_id", type=int)
@pass_context
@require_auth
def settings(ctx: DxsContext, branch_id: int) -> None:
    """Show application settings.

    Lists all application settings configured for a branch.

    \b
    Arguments:
        BRANCH_ID  Branch ID

    \b
    Example:
        dxs branch settings 100
    """
    client = ApiClient()
    ctx.log(f"Fetching settings for branch {branch_id}...")

    settings_data = client.get(BranchEndpoints.settings(branch_id))

    # Normalize to list if not already
    if not isinstance(settings_data, list):
        settings_data = [settings_data] if settings_data else []

    ctx.output(list_response(items=settings_data, semantic_key="settings", branch_id=branch_id))


@branch.command()
@click.argument("branch_id", type=int)
@pass_context
@require_auth
def operations(ctx: DxsContext, branch_id: int) -> None:
    """Show operations and workflows.

    Lists all operations and workflows defined for a branch.

    \b
    Arguments:
        BRANCH_ID  Branch ID

    \b
    Example:
        dxs branch operations 100
    """
    client = ApiClient()
    ctx.log(f"Fetching operations for branch {branch_id}...")

    operations_data = client.get(BranchEndpoints.operations(branch_id))

    # Normalize to list if not already
    if not isinstance(operations_data, list):
        operations_data = [operations_data] if operations_data else []

    ctx.output(
        list_response(items=operations_data, semantic_key="operations", branch_id=branch_id)
    )


@branch.command()
@click.argument("branch_id", type=int)
@pass_context
@require_auth
def replacements(ctx: DxsContext, branch_id: int) -> None:
    """Show configuration replacements.

    Lists all configuration replacements (customizations from component modules)
    for a branch.

    \b
    Arguments:
        BRANCH_ID  Branch ID

    \b
    Example:
        dxs branch replacements 100
    """
    client = ApiClient()
    ctx.log(f"Fetching replacements for branch {branch_id}...")

    replacements_data = client.get(BranchEndpoints.replacements(branch_id))

    # Normalize to list if not already
    if not isinstance(replacements_data, list):
        replacements_data = [replacements_data] if replacements_data else []

    ctx.output(
        list_response(items=replacements_data, semantic_key="replacements", branch_id=branch_id)
    )
