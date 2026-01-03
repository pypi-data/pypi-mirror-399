"""API endpoint path definitions for Datex Studio API.

Note: Paths are relative to the base URL (e.g., https://wavelength.host/api).
Do not include /api prefix as it's part of the base URL.
"""


class SourceControlEndpoints:
    """Source control API endpoints.

    Base: /sourcecontrol (relative to api_base_url)
    """

    @staticmethod
    def locks(repo_id: int) -> str:
        """Get all locks for a repository."""
        return f"/sourcecontrol/{repo_id}/locks"

    @staticmethod
    def history(repo_id: int) -> str:
        """Get commit history for a repository."""
        return f"/sourcecontrol/{repo_id}/history"

    @staticmethod
    def branch_history(branch_id: int) -> str:
        """Get commit history for a specific branch."""
        return f"/sourcecontrol/application/{branch_id}/history"

    @staticmethod
    def configuration_history(branch_id: int, reference_name: str) -> str:
        """Get version history for a specific configuration."""
        return f"/sourcecontrol/{branch_id}/configuration/{reference_name}/history"

    @staticmethod
    def upstream_changes(branch_id: int) -> str:
        """Get upstream (base branch) changes."""
        return f"/sourcecontrol/{branch_id}/upstreamChanges"

    @staticmethod
    def feature_branch_changes(branch_id: int) -> str:
        """Get feature branch changes compared to base."""
        return f"/sourcecontrol/{branch_id}/featureBranchChanges"

    @staticmethod
    def history_branch_changes(branch_id: int) -> str:
        """Get branch changes with commit details."""
        return f"/sourcecontrol/{branch_id}/historyBranchChanges"

    @staticmethod
    def replacements_history(branch_id: int) -> str:
        """Get history of configuration replacement changes."""
        return f"/sourcecontrol/{branch_id}/replacements/history"

    @staticmethod
    def settings_and_references_history(branch_id: int) -> str:
        """Get history of settings and references changes."""
        return f"/sourcecontrol/{branch_id}/settings-and-references/history"

    @staticmethod
    def operations_and_roles_history(branch_id: int) -> str:
        """Get history of operations and roles changes."""
        return f"/sourcecontrol/{branch_id}/operations-and-roles/history"

    # Lock operations (for future use)
    @staticmethod
    def lock_config(branch_id: int, reference_name: str) -> str:
        """Lock a specific configuration."""
        return f"/sourcecontrol/{branch_id}/config/{reference_name}/lock"

    @staticmethod
    def unlock_config(branch_id: int, reference_name: str) -> str:
        """Unlock a specific configuration."""
        return f"/sourcecontrol/{branch_id}/config/{reference_name}/unlock"

    @staticmethod
    def commit(branch_id: int) -> str:
        """Commit changes."""
        return f"/sourcecontrol/{branch_id}/commit"

    @staticmethod
    def pull(branch_id: int) -> str:
        """Pull changes from base branch."""
        return f"/sourcecontrol/{branch_id}/pull"

    @staticmethod
    def create_feature_branch(branch_id: int) -> str:
        """Create a feature branch."""
        return f"/sourcecontrol/{branch_id}/createFeatureBranch"


class OrganizationEndpoints:
    """Organization API endpoints."""

    @staticmethod
    def list() -> str:
        """List all organizations."""
        return "/organizations"

    @staticmethod
    def get(org_id: int) -> str:
        """Get organization by ID."""
        return f"/organizations/{org_id}"

    @staticmethod
    def mine() -> str:
        """Get current user's organization."""
        return "/organizations/mine"


class RepoEndpoints:
    """Repository (ApplicationDefinition) API endpoints."""

    @staticmethod
    def list(org_id: int | None = None) -> str:
        """List repositories, optionally filtered by organization."""
        if org_id:
            return f"/applicationdefinitions?organizationId={org_id}"
        return "/applicationdefinitions"

    @staticmethod
    def get(repo_id: int) -> str:
        """Get repository by ID."""
        return f"/applicationdefinitions/{repo_id}"


class BranchEndpoints:
    """Branch (Application) API endpoints."""

    @staticmethod
    def list(repo_id: int) -> str:
        """List branches by repository ID."""
        return f"/applications?applicationDefinitionId={repo_id}"

    @staticmethod
    def get(branch_id: int) -> str:
        """Get branch by ID."""
        return f"/applications/{branch_id}"

    @staticmethod
    def roles(branch_id: int) -> str:
        """Get branch roles."""
        return f"/applications/{branch_id}/roles"

    @staticmethod
    def shell(branch_id: int) -> str:
        """Get branch shell configuration."""
        return f"/applications/{branch_id}/shell"

    @staticmethod
    def validate(branch_id: int) -> str:
        """Validate branch."""
        return f"/applications/{branch_id}/validate"

    @staticmethod
    def candelete(branch_id: int) -> str:
        """Check if branch can be deleted."""
        return f"/applications/{branch_id}/candelete"

    @staticmethod
    def replacements(branch_id: int) -> str:
        """Get configuration replacements for a branch."""
        return f"/applications/{branch_id}/configurationreplacements"

    @staticmethod
    def settings(branch_id: int) -> str:
        """Get application settings for a branch."""
        return f"/applications/{branch_id}/settings"

    @staticmethod
    def operations(branch_id: int) -> str:
        """Get operations for a branch."""
        return f"/applications/{branch_id}/operations"


class UserEndpoints:
    """User API endpoints."""

    @staticmethod
    def list() -> str:
        """List all users."""
        return "/users"

    @staticmethod
    def get(user_id: int) -> str:
        """Get user by ID."""
        return f"/users/{user_id}"


class MarketplaceEndpoints:
    """Marketplace application and version API endpoints."""

    @staticmethod
    def list(org_id: int | None = None) -> str:
        """List marketplace applications, optionally filtered by organization."""
        if org_id:
            return f"/marketplaceapplications?organizationId={org_id}"
        return "/marketplaceapplications"

    @staticmethod
    def get(app_id: int) -> str:
        """Get marketplace application by ID."""
        return f"/marketplaceapplications/{app_id}"

    @staticmethod
    def versions(app_id: int) -> str:
        """List published versions of a marketplace application."""
        return f"/marketplaceapplications/{app_id}/versions"

    @staticmethod
    def version(version_id: int) -> str:
        """Get marketplace application version by ID."""
        return f"/marketplaceapplicationversions/{version_id}"


class DependencyEndpoints:
    """Application dependency (references) API endpoints."""

    @staticmethod
    def list(branch_id: int) -> str:
        """List direct dependencies for a branch."""
        return f"/applications/{branch_id}/references"

    @staticmethod
    def all_references(branch_id: int) -> str:
        """List all references including transitive dependencies."""
        return f"/applications/{branch_id}/allreferences"


class WorkitemEndpoints:
    """Application work items API endpoints."""

    @staticmethod
    def list(branch_id: int) -> str:
        """List work items linked to a branch."""
        return f"/applications/{branch_id}/applicationworkitems"


class ConfigurationEndpoints:
    """Configuration content API endpoints."""

    @staticmethod
    def list_all(branch_id: int, config_type: str) -> str:
        """List all configurations of a type for a branch."""
        return f"/applications/{branch_id}/{config_type}configurations"

    @staticmethod
    def get_content(branch_id: int, config_type: str, config_id: int) -> str:
        """Get configuration content by ID."""
        return f"/applications/{branch_id}/{config_type}configurations/{config_id}"

    @staticmethod
    def get_by_reference(branch_id: int, config_type: str, ref_name: str) -> str:
        """Get configuration by reference name."""
        return f"/applications/{branch_id}/{config_type}configurations/referenceName/{ref_name}"
