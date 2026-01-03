"""Document commands: dxs source document [build|resume|status|graph-only].

Build complete dependency graphs and extract raw configuration data for AI analysis.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import click
import yaml

from dxs.cli import DxsContext, pass_context
from dxs.core.api import ApiClient, BranchEndpoints, ConfigurationEndpoints, DependencyEndpoints
from dxs.core.auth import require_auth
from dxs.core.cache import get_cache
from dxs.core.graph import (
    DependencyGraph,
    DocumentProgress,
    GraphNode,
    NodeStatus,
    compute_depths,
    topological_sort,
)
from dxs.core.output.yaml_fmt import convert_code_to_literal
from dxs.utils.errors import ValidationError
from dxs.utils.responses import single

# Map trace reference types to semantic edge types for dependency graph
EDGE_TYPE_MAP: dict[str, str] = {
    # hosts - embedded components
    "grids": "hosts",
    "forms": "hosts",
    "widgets": "hosts",
    "cards": "hosts",
    "lists": "hosts",
    "hubs": "hosts",
    "editors": "hosts",
    "calendars": "hosts",
    "reports": "hosts",
    "visualizations": "hosts",
    # opens_dialog - components opened as dialogs
    "dialogs": "opens_dialog",
    # reads_data - data sources
    "datasources": "reads_data",
    "footprintdatasources": "reads_data",
    # calls_backend - backend invocations
    "backend_flows": "calls_backend",
    "footprintflows": "calls_backend",
    "apis": "calls_backend",
    "platform_apis": "calls_backend",
    "database_tables": "calls_backend",
    "scheduled_jobs": "calls_backend",
    # uses_selector - dropdown/lookup sources
    "selectors": "uses_selector",
    # checks_permission - security checks
    "operations": "checks_permission",
    # uses_type - custom type definitions
    "types": "uses_type",
    # uses_setting - configuration settings
    "settings": "uses_setting",
    "api_settings": "uses_setting",
}

# Reference types to skip (not edges to other configs)
SKIP_REFERENCE_TYPES = {"private_frontend_flows", "frontend_flows", "_dynamic_references"}


def _progress(message: str) -> None:
    """Print progress message immediately (always visible, not affected by quiet mode)."""
    import sys

    click.echo(message, err=True)
    sys.stderr.flush()


def _fetch_with_retry(
    client: ApiClient,
    endpoint: str,
    max_retries: int = 3,
    backoff_base: float = 1.0,
) -> tuple[dict[str, Any] | None, str | None]:
    """Fetch from API with retry logic for transient errors.

    Args:
        client: API client
        endpoint: API endpoint to call
        max_retries: Maximum number of retry attempts
        backoff_base: Base delay in seconds (doubles each retry)

    Returns:
        Tuple of (result, error_message). If successful, error is None.
        If failed after retries, result is None and error contains the message.
    """
    import time

    transient_codes = ("502", "503", "504", "timeout", "connection")
    last_error = ""

    for attempt in range(max_retries + 1):
        try:
            result = client.get(endpoint)
            return result, None
        except Exception as e:
            last_error = str(e)
            error_lower = last_error.lower()

            # Check if this is a transient error worth retrying
            is_transient = any(code in error_lower for code in transient_codes)

            if is_transient and attempt < max_retries:
                delay = backoff_base * (2**attempt)
                _progress(f"    Retry {attempt + 1}/{max_retries} after {delay:.1f}s: {last_error}")
                time.sleep(delay)
            else:
                # Non-transient error or final attempt
                break

    return None, last_error


def _fetch_config_cached(
    client: ApiClient,
    branch_id: int,
    config_type: str,
    config_id: int,
    branch_status: int,
    ref_name: str,
) -> tuple[dict[str, Any] | None, str | None, bool]:
    """Fetch config content with cache support.

    Args:
        client: API client
        branch_id: Branch ID containing the config
        config_type: Configuration type (grid, form, etc.)
        config_id: Configuration ID
        branch_status: Branch's applicationStatusId (for cache decisions)
        ref_name: Reference name (for cache storage)

    Returns:
        Tuple of (config, error, from_cache):
        - config: The configuration data, or None if failed
        - error: Error message if failed, None if successful
        - from_cache: True if result came from cache
    """
    cache = get_cache()

    # Check cache first
    cached = cache.get_config_content(branch_id, config_type, config_id)
    if cached is not None:
        return cached, None, True

    # Fetch from API with retry
    config, error = _fetch_with_retry(
        client,
        ConfigurationEndpoints.get_content(branch_id, config_type, config_id),
        max_retries=3,
        backoff_base=1.0,
    )

    if config is not None:
        # Store in cache (only if branch is cacheable/immutable)
        cache.set_config_content(branch_id, branch_status, config_type, config_id, ref_name, config)

    return config, error, False


def _filter_nulls(data: Any) -> Any:
    """Recursively remove null values and empty containers from data.

    Args:
        data: Input data (dict, list, or scalar)

    Returns:
        Cleaned data with nulls removed
    """
    if isinstance(data, dict):
        cleaned: dict[str, Any] = {}
        for key, value in data.items():
            if value is None:
                continue
            filtered = _filter_nulls(value)
            # Skip empty dicts and empty lists after filtering
            if filtered == {} or filtered == []:
                continue
            cleaned[key] = filtered
        return cleaned
    elif isinstance(data, list):
        cleaned_list: list[Any] = []
        for item in data:
            if item is None:
                continue
            filtered = _filter_nulls(item)
            # Keep empty dicts/lists in arrays (they might be meaningful placeholders)
            cleaned_list.append(filtered)
        return cleaned_list
    else:
        return data


def _get_explore_helpers() -> tuple:
    """Lazily import helpers from explore module to avoid circular imports."""
    from dxs.commands.explore import (
        CONFIGURATION_TYPES,
        _build_config_index,
        _extract_all_references,
        _get_json_content,
    )

    return CONFIGURATION_TYPES, _build_config_index, _extract_all_references, _get_json_content


def _fetch_library_branches(
    client: ApiClient, branch_id: int
) -> tuple[dict[str, int], dict[int, int]]:
    """Fetch ALL library references (direct + transitive) and build mapping of app_ref_name -> branch_id.

    Uses: GET /applications/{branch_id}/references
    This endpoint returns all references including transitive dependencies.

    Returns:
        Tuple of (library_branches, branch_statuses):
        - library_branches: app_ref_name -> branch_id
        - branch_statuses: branch_id -> applicationStatusId (for caching)
    """
    library_map: dict[str, int] = {}
    branch_statuses: dict[int, int] = {}

    try:
        refs = client.get(DependencyEndpoints.list(branch_id))
        if not isinstance(refs, list):
            refs = [refs] if refs else []

        for ref in refs:
            ref_name = ref.get("referenceName", "")
            app_id = ref.get("applicationId")
            if ref_name and app_id:
                library_map[ref_name] = app_id

        # Fetch branch statuses for all library branches (for caching decisions)
        for lib_branch_id in set(library_map.values()):
            try:
                branch_data = client.get(BranchEndpoints.get(lib_branch_id))
                status = branch_data.get("applicationStatusId", 0)
                branch_statuses[lib_branch_id] = status
            except Exception:
                branch_statuses[lib_branch_id] = 0  # Not cacheable if unknown

    except Exception:
        pass

    return library_map, branch_statuses


def _get_branch_app_name(client: ApiClient, branch_id: int) -> str:
    """Get the application name for a branch."""
    try:
        branch_data = client.get(BranchEndpoints.get(branch_id))
        app_def = branch_data.get("applicationDefinition", {})
        name = app_def.get("name")
        return str(name) if name else f"Branch {branch_id}"
    except Exception:
        return f"Branch {branch_id}"


def _extract_structure(config: dict[str, Any], config_type: str) -> dict[str, Any]:
    """Extract type-specific structural information from a config."""
    _, _, _, _get_json_content = _get_explore_helpers()
    json_content = _get_json_content(config)
    structure: dict[str, Any] = {}

    if config_type == "grid":
        # Extract datasource
        ds = json_content.get("datasource")
        if isinstance(ds, str):
            structure["datasource"] = ds
        elif isinstance(json_content.get("datasourceConfig"), dict):
            structure["datasource"] = json_content["datasourceConfig"].get("configId")

        # Extract toolbar actions
        toolbar = json_content.get("topToolbar") or json_content.get("toolbar") or []
        if toolbar:
            actions = []
            for item in toolbar:
                btn_cfg = item.get("buttonConfig") or item
                click_cfg = btn_cfg.get("clickFlowConfig") or {}
                actions.append(
                    {
                        "id": item.get("id"),
                        "label": btn_cfg.get("label"),
                        "flow": click_cfg.get("flowId"),
                    }
                )
            structure["toolbar_actions"] = actions

        # Extract filters
        filters = json_content.get("filters") or []
        if filters:
            structure["filters"] = [{"id": f.get("id"), "label": f.get("label")} for f in filters]

    elif config_type == "hub":
        # Extract tabs
        tabs = json_content.get("tabs") or []
        if tabs:
            structure["tabs"] = [
                {
                    "id": t.get("id"),
                    "title": t.get("title"),
                    "contentType": t.get("contentType"),
                    "configId": (t.get("contentConfig") or {}).get("configId"),
                }
                for t in tabs
            ]

        # Extract toolbar
        toolbar = json_content.get("toolbar") or []
        if toolbar:
            actions = []
            for item in toolbar:
                if item.get("type") == "button":
                    btn_cfg = item.get("buttonConfig") or {}
                    click_cfg = btn_cfg.get("clickFlowConfig") or {}
                    actions.append(
                        {
                            "id": item.get("id"),
                            "label": btn_cfg.get("label"),
                            "flow": click_cfg.get("flowId"),
                        }
                    )
            structure["toolbar_actions"] = actions

        # Extract filters
        filters = json_content.get("filters") or []
        if filters:
            structure["filters"] = [{"id": f.get("id"), "label": f.get("label")} for f in filters]

        # Extract widgets
        widgets = json_content.get("widgets") or []
        if widgets:
            structure["widgets"] = [
                {"id": w.get("id"), "configId": (w.get("widgetConfig") or {}).get("configId")}
                for w in widgets
            ]

    elif config_type == "shell":
        # Extract home view
        home = json_content.get("home")
        if isinstance(home, dict):
            structure["home"] = home.get("viewConfig", {}).get("configId")

        # Extract menubar
        menubar = json_content.get("menubar") or []
        if menubar:
            structure["menubar"] = [
                {
                    "id": m.get("id"),
                    "label": m.get("label"),
                    "items": [
                        {"id": i.get("id"), "label": i.get("label")} for i in m.get("items", [])
                    ],
                }
                for m in menubar
            ]

    elif config_type == "form":
        # Extract fieldsets and fields
        fieldsets = json_content.get("fieldsets") or []
        if fieldsets:
            structure["fieldsets"] = [
                {
                    "id": fs.get("id"),
                    "label": fs.get("label"),
                    "fields": [
                        {"id": f.get("id"), "label": f.get("label"), "type": f.get("type")}
                        for f in fs.get("fields", [])
                    ],
                }
                for fs in fieldsets
            ]

        # Extract toolbar
        toolbar = json_content.get("toolbar") or []
        if toolbar:
            structure["toolbar"] = [
                {"id": t.get("id"), "label": t.get("buttonConfig", {}).get("label")}
                for t in toolbar
            ]

    elif config_type == "datasource":
        structure["type"] = json_content.get("type")
        structure["apiSettingName"] = json_content.get("apiSettingName")
        if paths := json_content.get("paths"):
            structure["paths"] = paths
        if query_opts := json_content.get("queryOptions"):
            structure["queryOptions"] = query_opts

    elif config_type in ("flow", "frontendflow", "footprintflow"):
        structure["flowType"] = json_content.get("flowType") or json_content.get("type")
        if inputs := json_content.get("inputParams") or json_content.get("inParams"):
            structure["inputs"] = [{"id": p.get("id"), "type": p.get("type")} for p in inputs]
        if outputs := json_content.get("outputParams") or json_content.get("outParams"):
            structure["outputs"] = [{"id": p.get("id"), "type": p.get("type")} for p in outputs]

    return structure


def build_dependency_graph(
    client: ApiClient,
    branch_id: int,
    ctx: DxsContext,
    target: str | None = None,
    max_depth: int = 10,
    include_external: bool = True,
) -> DependencyGraph:
    """Build complete dependency graph starting from shell(s) or target config.

    Args:
        client: API client
        branch_id: Main branch ID
        ctx: CLI context for logging
        target: Optional starting config reference name (default: all shells)
        max_depth: Maximum traversal depth
        include_external: Whether to include external configs

    Returns:
        DependencyGraph with all discovered nodes and edges
    """
    _, _build_config_index, _extract_all_references, _ = _get_explore_helpers()

    app_name = _get_branch_app_name(client, branch_id)
    graph = DependencyGraph(branch_id=branch_id, app_name=app_name, target=target)

    # Step 1: Get library branch mappings and statuses (for caching)
    _progress("  Fetching library references...")
    graph.library_branches, graph.branch_statuses = _fetch_library_branches(client, branch_id)
    _progress(f"  Found {len(graph.library_branches)} library references")

    # Also get the main branch's status for caching
    try:
        main_branch_data = client.get(BranchEndpoints.get(branch_id))
        graph.branch_statuses[branch_id] = main_branch_data.get("applicationStatusId", 0)
    except Exception:
        graph.branch_statuses[branch_id] = 0  # Not cacheable if unknown

    # Step 2: Build config index (captures ALL configs in branch)
    _progress("  Building configuration index...")
    config_index = _build_config_index(client, branch_id, ctx)
    graph._full_index = config_index.copy()
    _progress(f"  Indexed {len(config_index)} total configurations")

    # Track visited and in-stack for cycle detection
    visited: set[str] = set()
    in_stack: set[str] = set()
    roots: list[str] = []
    nodes_discovered = [0]  # Use list to allow mutation in nested function
    fetch_failures: list[tuple[str, str, str]] = []  # (ref_name, config_type, error)

    _progress("")
    _progress("  Traversing dependency graph (DFS)...")

    def dfs(ref_name: str, depth: int) -> None:
        key = ref_name.lower()

        if depth > max_depth:
            return

        if key in visited:
            return

        # Cycle detection
        if key in in_stack:
            # Mark as cycle participant
            if key in graph.nodes:
                graph.nodes[key].in_cycle = True
            return

        visited.add(key)
        in_stack.add(key)

        # Lookup config in index
        lookup = config_index.get(key)
        if not lookup:
            in_stack.discard(key)
            return

        config_type, config_id, app_ref, is_external = lookup

        # Skip external if not included
        if not include_external and is_external:
            in_stack.discard(key)
            return

        if not config_id:
            in_stack.discard(key)
            return

        # Determine source branch for external configs
        source_branch = branch_id
        if is_external and app_ref:
            source_branch = graph.library_branches.get(app_ref, branch_id)

        # Fetch config content with retry logic
        config, fetch_error = _fetch_with_retry(
            client,
            ConfigurationEndpoints.get_content(source_branch, config_type, config_id),
            max_retries=3,
            backoff_base=1.0,
        )
        if config is None:
            _progress(f"    Warning: Failed to fetch {ref_name} after retries: {fetch_error}")
            fetch_failures.append((ref_name, config_type, fetch_error or "Unknown error"))
            in_stack.discard(key)
            return

        # Create node
        label = config.get("label") or config.get("title") or config.get("referenceName")
        node = GraphNode(
            reference_name=ref_name,
            config_type=config_type,
            config_id=config_id,
            branch_id=source_branch,
            application_ref_name=app_ref,
            is_external=is_external,
            label=label,
            depth=depth,
        )
        graph.add_node(node)
        nodes_discovered[0] += 1

        # Log progress every 10 nodes or for important types
        if nodes_discovered[0] % 10 == 0 or config_type in ("shell", "hub"):
            source_info = f"[{app_ref}]" if is_external else "[owned]"
            _progress(
                f"    Discovered {nodes_discovered[0]:4d} | depth {depth} | {config_type:12s} | {ref_name} {source_info}"
            )

        # Extract and traverse references
        refs = _extract_all_references(config, config_type, config_index)

        for ref_type, ref_list in refs.items():
            edge_type = ref_type.rstrip("s")  # datasources -> datasource
            for ref in ref_list:
                ref_lookup = config_index.get(ref.lower())
                if ref_lookup:
                    ref_cfg_type, ref_id, ref_app, ref_is_external = ref_lookup

                    # Skip external if not included
                    if not include_external and ref_is_external:
                        continue

                    graph.add_edge(ref_name, ref, edge_type)
                    dfs(ref, depth + 1)

        in_stack.discard(key)

    # Step 3: Determine starting points and traverse
    if target:
        # Start from specific target config
        _progress(f"  Starting from target: {target}")
        roots = [target]
        dfs(target, 0)
    else:
        # Start from all shells
        _progress("  Finding entry points (shells)...")
        try:
            shells = client.get(ConfigurationEndpoints.list_all(branch_id, "shell"))
            if not isinstance(shells, list):
                shells = [shells] if shells else []

            _progress(f"  Found {len(shells)} shell(s)")
            for shell in shells:
                shell_is_external = shell.get("isExternal", False)
                if not include_external and shell_is_external:
                    continue
                ref_name = shell.get("referenceName", "")
                if ref_name:
                    roots.append(ref_name)
                    dfs(ref_name, 0)
        except Exception as e:
            _progress(f"  Error fetching shells: {e}")

    _progress("")
    _progress(f"  DFS complete: {len(graph.nodes)} nodes discovered")

    # Report fetch failures
    if fetch_failures:
        _progress("")
        _progress(f"  Fetch Failures ({len(fetch_failures)} configs):")
        for ref_name, cfg_type, error in fetch_failures[:5]:
            _progress(f"    - {cfg_type}: {ref_name}")
            _progress(f"      Error: {error}")
        if len(fetch_failures) > 5:
            _progress(f"    ... and {len(fetch_failures) - 5} more")
        _progress("")

    # Step 4: Compute depths from roots
    _progress("  Computing node depths...")
    compute_depths(graph, roots)

    # Step 5: Compute unreachable configs
    _progress("  Identifying unreachable configs...")
    graph.compute_unreachable()

    _progress(f"  Unreachable: {len(graph.unreachable)} configs not reachable from entry point(s)")

    return graph


def _write_yaml_file(path: Path, data: dict[str, Any]) -> None:
    """Write data to YAML file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)


def _write_libraries_simple(
    output_dir: Path, branch_id: int, library_branches: dict[str, int]
) -> Path:
    """Write library references index (simplified version)."""
    path = output_dir / "libraries.yaml"
    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "branch_id": branch_id,
        "count": len(library_branches),
        "libraries": library_branches,
    }
    _write_yaml_file(path, data)
    return path


def _write_config_file_simple(
    config: dict[str, Any],
    config_type: str,
    ref_name: str,
    branch_id: int,
    lib_name: str | None,
    output_dir: Path,
    get_json_content_fn: Any,
) -> Path:
    """Write individual config file (simplified version without GraphNode).

    Args:
        config: Full configuration data from API
        config_type: Configuration type (grid, form, etc.)
        ref_name: Configuration reference name
        branch_id: Source branch ID
        lib_name: Library name if external, None if local
        output_dir: Base output directory
        get_json_content_fn: Function to extract JSON content from config

    Returns:
        Path to the written file
    """
    # Determine output path
    if lib_name:
        # External config from library
        path = output_dir / lib_name / str(branch_id) / config_type / f"{ref_name}.yaml"
    else:
        # Local config
        path = output_dir / "local" / config_type / f"{ref_name}.yaml"

    # Extract structure
    structure = _extract_structure(config, config_type)

    # Build output data with code fields converted to literal strings for readability
    raw_config = _filter_nulls(get_json_content_fn(config))
    raw_config = convert_code_to_literal(raw_config)

    label = config.get("label") or config.get("title") or config.get("referenceName")

    data = {
        "reference_name": ref_name,
        "config_type": config_type,
        "config_id": config.get("id"),
        "source_branch_id": branch_id,
        "source_library": lib_name,
        "is_external": lib_name is not None,
        "label": label,
        "documented_at": datetime.now(timezone.utc).isoformat(),
        "raw_config": raw_config,
        "structure": _filter_nulls(structure),
    }

    _write_yaml_file(path, data)
    return path


def _write_info_yaml(
    output_dir: Path,
    branch_id: int,
    app_name: str,
    library_branches: dict[str, int],
    type_counts: dict[str, int],
    library_type_counts: dict[str, dict[str, int]],
) -> Path:
    """Write application info file."""
    path = output_dir / "info.yaml"

    # Calculate local counts (total minus library counts)
    local_counts: dict[str, int] = {}
    for ctype, total in type_counts.items():
        lib_total = sum(lib_counts.get(ctype, 0) for lib_counts in library_type_counts.values())
        local_count = total - lib_total
        if local_count > 0:
            local_counts[ctype] = local_count

    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "application": {
            "name": app_name,
            "branch_id": branch_id,
        },
        "libraries": list(library_branches.keys()),
        "config_counts": {
            "local": local_counts,
            "by_library": library_type_counts,
            "total_local": sum(local_counts.values()),
            "total_library": sum(type_counts.values()) - sum(local_counts.values()),
            "total": sum(type_counts.values()),
        },
    }
    _write_yaml_file(path, data)
    return path


def _write_dependency_graph(graph: DependencyGraph, output_dir: Path) -> Path:
    """Write dependency graph to YAML file."""
    path = output_dir / "graph" / "dependency-graph.yaml"
    _write_yaml_file(path, graph.to_dict())
    return path


def _write_dependency_graph_with_missing(
    graph: DependencyGraph,
    missing_references: dict[str, list[dict[str, str]]],
    cycle_nodes: list[str],
    output_dir: Path,
) -> Path:
    """Write dependency graph to YAML file with missing references and cycle info."""
    path = output_dir / "graph" / "dependency-graph.yaml"

    # Start with base graph data
    data = graph.to_dict()

    # Add cycle info to summary
    data["summary"]["cycles_count"] = len(cycle_nodes)

    # Add missing references section
    total_missing = sum(len(refs) for refs in missing_references.values())
    data["summary"]["missing_references_count"] = total_missing

    if missing_references:
        data["missing_references"] = {
            "count": total_missing,
            "by_source": dict(sorted(missing_references.items())),
        }

    # Add cycle nodes list
    if cycle_nodes:
        data["cycles"] = {
            "count": len(cycle_nodes),
            "nodes": cycle_nodes,
        }

    _write_yaml_file(path, data)
    return path


def _write_topological_order(
    graph: DependencyGraph, sorted_order: list[str], cycle_nodes: list[str], output_dir: Path
) -> Path:
    """Write topological order to YAML file."""
    path = output_dir / "graph" / "topological-order.yaml"

    order_data = []
    reverse_adj = graph.get_reverse_adjacency()

    for ref_key in sorted_order:
        node = graph.nodes.get(ref_key)
        if node:
            order_data.append(
                {
                    "reference_name": node.reference_name,
                    "config_type": node.config_type,
                    "depth": node.depth,
                    "in_cycle": node.in_cycle,
                    "depended_by": reverse_adj.get(ref_key, []),
                }
            )

    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_configs": len(sorted_order),
        "cycle_count": len(cycle_nodes),
        "order": order_data,
    }

    if cycle_nodes:
        data["cycles"] = {
            "participants": cycle_nodes,
            "break_point": cycle_nodes[0] if cycle_nodes else None,
        }

    _write_yaml_file(path, data)
    return path


def _write_progress(progress: DocumentProgress, output_dir: Path) -> Path:
    """Write progress tracking file."""
    path = output_dir / "graph" / "progress.yaml"
    _write_yaml_file(path, progress.to_dict())
    return path


def _write_libraries(graph: DependencyGraph, output_dir: Path) -> Path:
    """Write library references index."""
    path = output_dir / "libraries.yaml"
    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "branch_id": graph.branch_id,
        "count": len(graph.library_branches),
        "libraries": graph.library_branches,
    }
    _write_yaml_file(path, data)
    return path


def _get_config_output_path(
    base_dir: Path,
    node: GraphNode,
    library_branches: dict[str, int],
) -> Path:
    """Generate output path based on config origin.

    Args:
        base_dir: Base output directory
        node: GraphNode with config metadata
        library_branches: Mapping of library names to branch IDs

    Returns:
        Path for the config file:
        - Local configs: base_dir/local/<type>/<ref_name>.yaml
        - External configs: base_dir/<LibraryName>/<BranchId>/<type>/<ref_name>.yaml
    """
    if node.is_external:
        lib_name = node.application_ref_name or "unknown"
        lib_branch = library_branches.get(lib_name, node.branch_id)
        return (
            base_dir / lib_name / str(lib_branch) / node.config_type / f"{node.reference_name}.yaml"
        )
    else:
        return base_dir / "local" / node.config_type / f"{node.reference_name}.yaml"


def _write_config_file(
    client: ApiClient,
    node: GraphNode,
    config_index: dict[str, tuple[str, int, str, bool]],
    output_dir: Path,
    library_branches: dict[str, int],
    branch_statuses: dict[int, int],
) -> tuple[Path, bool]:
    """Write individual config file with raw data and extracted structure.

    Returns:
        Tuple of (output_path, from_cache) indicating if config came from cache.
    """
    _, _, _extract_all_references, _get_json_content = _get_explore_helpers()

    # Get branch status for caching (0 = unknown/not cacheable)
    branch_status = branch_statuses.get(node.branch_id, 0)

    # Fetch full config with caching support
    config, error, from_cache = _fetch_config_cached(
        client,
        node.branch_id,
        node.config_type,
        node.config_id,
        branch_status,
        node.reference_name,
    )
    if config is None:
        raise RuntimeError(f"Failed to fetch config after retries: {error}")

    # Extract structure
    structure = _extract_structure(config, node.config_type)

    # Extract dependencies
    refs = _extract_all_references(config, node.config_type, config_index)

    # Build output data with code fields converted to literal strings for readability
    raw_config = _filter_nulls(_get_json_content(config))
    raw_config = convert_code_to_literal(raw_config)  # Convert code fields to YAML literal blocks

    data = {
        "reference_name": node.reference_name,
        "config_type": node.config_type,
        "config_id": node.config_id,
        "source_branch_id": node.branch_id,
        "source_library": node.application_ref_name or None,
        "is_external": node.is_external,
        "label": node.label,
        "documented_at": datetime.now(timezone.utc).isoformat(),
        "raw_config": raw_config,
        "structure": _filter_nulls(structure),
        "dependencies": refs,
    }

    # Write to origin-based directory structure
    path = _get_config_output_path(output_dir, node, library_branches)
    _write_yaml_file(path, data)

    return path, from_cache


def _load_graph(output_dir: Path) -> DependencyGraph | None:
    """Load existing graph from file."""
    path = output_dir / "graph" / "dependency-graph.yaml"
    if not path.exists():
        return None

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return DependencyGraph.from_dict(data)


def _load_progress(output_dir: Path) -> DocumentProgress | None:
    """Load existing progress from file."""
    path = output_dir / "graph" / "progress.yaml"
    if not path.exists():
        return None

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return DocumentProgress.from_dict(data)


@click.group()
def document() -> None:
    """Document application configurations.

    Downloads all configurations from a branch and its library dependencies
    (both direct and transitive references).

    \b
    Output Structure (build command):
        output_dir/
          local/<type>/<ref_name>.yaml      # Owned configs
          <LibraryName>/<BranchId>/<type>/  # Library configs
          libraries.yaml                     # Library references index
          info.yaml                          # Application info

    \b
    Examples:
        dxs source document build --branch 63588
        dxs source document build --branch 63588 -o ./custom/path --force
        dxs source document status --output-dir ./docs
    """
    pass


@document.command("build")
@click.option("--branch", "-b", type=int, required=True, help="Branch ID")
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(),
    default=None,
    help="Output directory (default: exploration/<AppName>/<BranchId>)",
)
@click.option("--force", "-f", is_flag=True, help="Overwrite existing output directory")
@pass_context
@require_auth
def build(
    ctx: DxsContext,
    branch: int,
    output_dir: str | None,
    force: bool,
) -> None:
    """Download all configurations from the branch and its library dependencies.

    \b
    This command downloads EVERY configuration from:
    1. The main branch (owned configs)
    2. ALL referenced libraries (direct and transitive)

    \b
    Output structure:
        <output_dir>/
        ├── local/<type>/<ref_name>.yaml      # Owned configs
        ├── <LibraryName>/<BranchId>/<type>/  # Library configs
        ├── libraries.yaml                     # Library references index
        └── info.yaml                          # Application info

    \b
    Examples:
        dxs source document build --branch 63588
        dxs source document build --branch 63588 -o ./custom/path
        dxs source document build --branch 63588 --force
    """
    CONFIGURATION_TYPES, _, _, _get_json_content = _get_explore_helpers()

    branch_id = branch

    # Connect to API first (needed for auto-generating output dir)
    _progress("")
    _progress("=" * 60)
    _progress("DXS SOURCE DOCUMENT - Build")
    _progress("=" * 60)
    _progress(f"  Branch ID: {branch_id}")
    _progress("")
    _progress("Connecting to API...")
    client = ApiClient()
    start_time = datetime.now(timezone.utc)

    # Get application info
    app_name = _get_branch_app_name(client, branch_id)

    # Auto-generate output directory if not specified
    if output_dir is None:
        # Sanitize app name for filesystem
        safe_app_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in app_name)
        out_path = Path("exploration") / safe_app_name / str(branch_id)
        _progress(f"  Auto-generated output: {out_path}")
    else:
        out_path = Path(output_dir)

    _progress(f"  Output: {out_path}")
    _progress(f"  Application: {app_name}")
    _progress("")

    # Check if output exists
    if out_path.exists() and not force:
        libraries_path = out_path / "libraries.yaml"
        if libraries_path.exists():
            raise ValidationError(
                f"Output directory {out_path} already exists. Use --force to overwrite.",
                code="DXS-DOC-001",
            )

    # Phase 1: Fetch all library references (direct + transitive)
    _progress("")
    _progress("-" * 60)
    _progress("PHASE 1/2: Discovering Libraries")
    _progress("-" * 60)
    _progress("  Fetching all library references (including transitive)...")

    library_branches, branch_statuses = _fetch_library_branches(client, branch_id)

    # Also get the main branch's status for caching
    try:
        main_branch_data = client.get(BranchEndpoints.get(branch_id))
        branch_statuses[branch_id] = main_branch_data.get("applicationStatusId", 0)
    except Exception:
        branch_statuses[branch_id] = 0  # Not cacheable if unknown

    _progress(f"  Found {len(library_branches)} library references:")
    for lib_name, lib_branch in sorted(library_branches.items()):
        _progress(f"    - {lib_name} (branch {lib_branch})")
    _progress("")

    # Write libraries.yaml
    _write_libraries_simple(out_path, branch_id, library_branches)

    # Phase 2: Download all configurations
    _progress("")
    _progress("-" * 60)
    _progress("PHASE 2/2: Downloading Configurations")
    _progress("-" * 60)

    files_created = 0
    failed_count = 0
    type_counts: dict[str, int] = {}
    library_type_counts: dict[str, dict[str, int]] = {}  # lib_name -> {type: count}

    # Build list of all branches to process: main branch + all libraries
    branches_to_process: list[tuple[int, str | None, bool]] = [
        (branch_id, None, False),  # main branch, no lib name, is_local=True
    ]
    for lib_name, lib_branch_id in library_branches.items():
        branches_to_process.append((lib_branch_id, lib_name, True))

    total_branches = len(branches_to_process)

    for branch_idx, (current_branch_id, current_lib_name, is_library) in enumerate(branches_to_process):
        source_label: str = current_lib_name if current_lib_name else "local"
        _progress("")
        _progress(
            f"  [{branch_idx + 1}/{total_branches}] Processing {source_label} (branch {current_branch_id})"
        )

        branch_status = branch_statuses.get(current_branch_id, 0)
        branch_files = 0
        branch_failures = 0

        if is_library and current_lib_name:
            library_type_counts[current_lib_name] = {}

        for ctype in CONFIGURATION_TYPES:
            try:
                # List all configs of this type in the branch
                configs_list = client.get(ConfigurationEndpoints.list_all(current_branch_id, ctype))
                if not isinstance(configs_list, list):
                    configs_list = [configs_list] if configs_list else []

                if not configs_list:
                    continue

                # Only include owned configs (isExternal=False)
                # Each branch should only save its own configs, not referenced ones
                configs_list = [c for c in configs_list if not c.get("isExternal", False)]

                if not configs_list:
                    continue

                _progress(f"    {ctype}: {len(configs_list)} configs")

                for cfg in configs_list:
                    cfg_id = cfg.get("id")
                    ref_name = cfg.get("referenceName", f"config_{cfg_id}")

                    if not cfg_id:
                        continue

                    try:
                        # Fetch full config content
                        config, error, from_cache = _fetch_config_cached(
                            client, current_branch_id, ctype, cfg_id, branch_status, ref_name
                        )

                        if config is None:
                            _progress(f"      ERROR: {ref_name}: {error}")
                            failed_count += 1
                            branch_failures += 1
                            continue

                        # Write config file
                        _write_config_file_simple(
                            config,
                            ctype,
                            ref_name,
                            current_branch_id,
                            current_lib_name,
                            out_path,
                            _get_json_content,
                        )

                        files_created += 1
                        branch_files += 1

                        # Track counts
                        type_counts[ctype] = type_counts.get(ctype, 0) + 1
                        if is_library and current_lib_name:
                            library_type_counts[current_lib_name][ctype] = (
                                library_type_counts[current_lib_name].get(ctype, 0) + 1
                            )

                    except Exception as e:
                        _progress(f"      ERROR: {ref_name}: {e}")
                        failed_count += 1
                        branch_failures += 1

            except Exception as e:
                ctx.log(f"    Error fetching {ctype} from branch {current_branch_id}: {e}")

        cache_indicator = " (cached)" if branch_status > 0 else ""
        _progress(
            f"    Completed: {branch_files} files, {branch_failures} failures{cache_indicator}"
        )

    # Write application info
    _write_info_yaml(
        out_path, branch_id, app_name, library_branches, type_counts, library_type_counts
    )

    # Calculate elapsed time
    end_time = datetime.now(timezone.utc)
    elapsed = end_time - start_time
    elapsed_str = str(elapsed).split(".")[0]  # Remove microseconds

    # Print summary
    _progress("")
    _progress("=" * 60)
    _progress("COMPLETE")
    _progress("=" * 60)
    _progress(f"  Application: {app_name}")
    _progress(f"  Elapsed time: {elapsed_str}")
    _progress("")
    _progress("  Summary:")
    _progress(f"    Total files created: {files_created}")
    _progress(f"    Failed: {failed_count}")
    _progress(f"    Libraries processed: {len(library_branches)}")
    _progress("")
    _progress("  Configs by Type:")
    for ctype, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        _progress(f"    {ctype:20s}: {count:4d}")
    _progress("")
    _progress(f"  Output directory: {out_path.absolute()}")
    _progress("")

    output = {
        "output_dir": str(out_path.absolute()),
        "branch_id": branch_id,
        "app_name": app_name,
        "summary": {
            "files_created": files_created,
            "failed": failed_count,
            "libraries": len(library_branches),
            "by_type": type_counts,
        },
        "library_summary": library_type_counts,
    }

    ctx.output(single(item=output, semantic_key="documentation", branch_id=branch_id))


@document.command("resume")
@click.option(
    "--output-dir", "-o", type=click.Path(exists=True), required=True, help="Output directory"
)
@pass_context
@require_auth
def resume(ctx: DxsContext, output_dir: str) -> None:
    """Resume documentation from last checkpoint.

    Loads progress.yaml and continues from the first pending config.

    \b
    Example:
        dxs source document resume -o ./exploration/footprint
    """
    out_path = Path(output_dir)

    # Load existing state
    graph = _load_graph(out_path)
    if not graph:
        raise ValidationError(
            f"No dependency graph found in {output_dir}. Run 'build' first.",
            code="DXS-DOC-002",
        )

    progress = _load_progress(out_path)
    if not progress:
        raise ValidationError(
            f"No progress file found in {output_dir}. Run 'build' first.",
            code="DXS-DOC-003",
        )

    if progress.status == "completed":
        _progress("Documentation already completed.")
        ctx.output(
            single(
                item={"status": "completed", "message": "All configs documented"},
                semantic_key="resume",
            )
        )
        return

    client = ApiClient()
    branch_id = graph.branch_id
    start_time = datetime.now(timezone.utc)

    # Calculate current progress
    completed_count = sum(
        1 for s in progress.config_status.values() if s.get("status") == "completed"
    )
    remaining = progress.total_configs - completed_count

    _progress("")
    _progress("=" * 60)
    _progress("DXS SOURCE DOCUMENT - Resume")
    _progress("=" * 60)
    _progress(f"  Application: {graph.app_name}")
    _progress(
        f"  Progress: {completed_count}/{progress.total_configs} completed ({remaining} remaining)"
    )
    _progress("")

    # Build config index
    _progress("  Building config index...")
    _, _build_config_index_fn, _, _ = _get_explore_helpers()
    config_index = _build_config_index_fn(client, branch_id, ctx)

    # Find first pending config
    start_index = 0
    for i, ref_key in enumerate(progress.processing_order):
        status = progress.config_status.get(ref_key, {}).get("status", "pending")
        if status == "pending":
            start_index = i
            break

    _progress(f"  Starting from index {start_index}: {progress.processing_order[start_index]}")
    _progress("")

    files_created = 0
    failed_count = 0
    total = len(progress.processing_order)

    for i in range(start_index, len(progress.processing_order)):
        ref_key = progress.processing_order[i]
        node = graph.get_node(ref_key)
        if not node:
            continue

        status = progress.config_status.get(ref_key, {}).get("status", "pending")
        if status in ("completed", "skipped"):
            continue

        # Progress indicator
        pct = ((i + 1) / total) * 100
        source_info = f" [{node.application_ref_name}]" if node.is_external else " [owned]"
        _progress(
            f"  [{i + 1:3d}/{total}] {pct:5.1f}% | {node.config_type:12s} | {node.reference_name}{source_info}"
        )

        # Update progress
        progress.current_index = i
        progress.config_status[ref_key]["status"] = "in_progress"
        progress.updated_at = datetime.now(timezone.utc).isoformat()
        _write_progress(progress, out_path)

        try:
            config_path, from_cache = _write_config_file(
                client, node, config_index, out_path, graph.library_branches, graph.branch_statuses
            )
            node.status = NodeStatus.COMPLETED
            node.output_file = str(config_path.relative_to(out_path))

            progress.config_status[ref_key]["status"] = "completed"
            progress.config_status[ref_key]["output_file"] = node.output_file
            progress.config_status[ref_key]["from_cache"] = from_cache
            files_created += 1

        except Exception as e:
            _progress(f"           ERROR: {e}")
            node.status = NodeStatus.FAILED
            node.error_message = str(e)
            progress.config_status[ref_key]["status"] = "failed"
            progress.config_status[ref_key]["error"] = str(e)
            failed_count += 1

    # Finalize extraction phase
    progress.status = "completed"
    progress.extraction_status = "completed"
    progress.updated_at = datetime.now(timezone.utc).isoformat()
    _write_progress(progress, out_path)
    _write_dependency_graph(graph, out_path)

    # Calculate elapsed time
    end_time = datetime.now(timezone.utc)
    elapsed = end_time - start_time
    elapsed_str = str(elapsed).split(".")[0]

    # Summary
    _progress("")
    _progress("=" * 60)
    _progress("RESUME COMPLETE")
    _progress("=" * 60)
    _progress(f"  Elapsed time: {elapsed_str}")
    _progress(f"  Files created this run: {files_created}")
    _progress(f"  Failed this run: {failed_count}")
    _progress(f"  Total completed: {completed_count + files_created}/{progress.total_configs}")
    _progress("")

    output = {
        "status": "completed",
        "files_created": files_created,
        "failed": failed_count,
        "total_configs": progress.total_configs,
    }

    ctx.output(single(item=output, semantic_key="resume", branch_id=branch_id))


@document.command("status")
@click.option(
    "--output-dir", "-o", type=click.Path(exists=True), required=True, help="Output directory"
)
@pass_context
def status(ctx: DxsContext, output_dir: str) -> None:
    """Show documentation progress status.

    \b
    Example:
        dxs source document status -o ./exploration/footprint
    """
    out_path = Path(output_dir)

    graph = _load_graph(out_path)
    if not graph:
        raise ValidationError(
            f"No dependency graph found in {output_dir}.",
            code="DXS-DOC-002",
        )

    progress = _load_progress(out_path)
    if not progress:
        raise ValidationError(
            f"No progress file found in {output_dir}.",
            code="DXS-DOC-003",
        )

    # Count statuses
    completed = sum(1 for s in progress.config_status.values() if s.get("status") == "completed")
    failed = sum(1 for s in progress.config_status.values() if s.get("status") == "failed")
    pending = progress.total_configs - completed - failed

    # Current config
    current_ref = None
    if progress.current_index < len(progress.processing_order):
        current_ref = progress.processing_order[progress.current_index]

    # Next few configs
    next_configs = []
    for i in range(
        progress.current_index + 1, min(progress.current_index + 4, len(progress.processing_order))
    ):
        next_configs.append(progress.processing_order[i])

    # Count cycles
    cycle_count = sum(1 for node in graph.nodes.values() if node.in_cycle)

    output = {
        "progress": {
            "status": progress.status,
            "total_configs": progress.total_configs,
            "completed": completed,
            "pending": pending,
            "failed": failed,
            "percent_complete": round(completed / progress.total_configs * 100, 1)
            if progress.total_configs > 0
            else 0,
        },
        "current_config": {
            "reference_name": current_ref,
            "index": progress.current_index,
        }
        if current_ref
        else None,
        "next_configs": next_configs,
        "cycles": {
            "count": cycle_count,
        },
        "unreachable": {
            "count": len(graph.unreachable),
        },
        "metadata": {
            "started_at": progress.started_at,
            "updated_at": progress.updated_at,
        },
    }

    ctx.output(single(item=output, semantic_key="status"))


@document.command("graph-only")
@click.option("--branch", "-b", type=int, required=True, help="Branch ID")
@click.option("--output-dir", "-o", type=click.Path(), required=True, help="Output directory")
@click.option("--target", "-t", type=str, default=None, help="Starting config reference name")
@click.option("--max-depth", "-d", type=int, default=10, help="Maximum traversal depth")
@click.option("--include-external/--owned-only", default=True, help="Include external configs")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing output")
@pass_context
@require_auth
def graph_only(
    ctx: DxsContext,
    branch: int,
    output_dir: str,
    target: str | None,
    max_depth: int,
    include_external: bool,
    force: bool,
) -> None:
    """Build dependency graph without extracting configs.

    Useful for quick analysis or when configs were already extracted.

    \b
    Example:
        dxs source document graph-only --branch 63588 -o ./exploration
        dxs source document graph-only --branch 63588 -o ./docs --target my_hub
    """
    branch_id = branch
    out_path = Path(output_dir)

    # Check if output exists
    if out_path.exists() and not force:
        graph_path = out_path / "graph" / "dependency-graph.yaml"
        if graph_path.exists():
            raise ValidationError(
                f"Graph already exists in {output_dir}. Use --force to overwrite.",
                code="DXS-DOC-001",
            )

    client = ApiClient()

    # Build the dependency graph
    _progress(f"Building dependency graph for branch {branch_id}...")
    graph = build_dependency_graph(
        client=client,
        branch_id=branch_id,
        ctx=ctx,
        target=target,
        max_depth=max_depth,
        include_external=include_external,
    )

    # Perform topological sort
    _progress("Performing topological sort...")
    sorted_order, cycle_nodes = topological_sort(graph)

    if cycle_nodes:
        _progress(f"Warning: {len(cycle_nodes)} configs form cycles")

    # Write graph files only
    _progress("Writing graph files...")
    _write_dependency_graph(graph, out_path)
    _write_topological_order(graph, sorted_order, cycle_nodes, out_path)
    _write_libraries(graph, out_path)

    # Count by type
    type_counts: dict[str, int] = {}
    for node in graph.nodes.values():
        type_counts[node.config_type] = type_counts.get(node.config_type, 0) + 1

    output = {
        "output_dir": str(out_path.absolute()),
        "branch_id": branch_id,
        "app_name": graph.app_name,
        "target": target,
        "graph_summary": {
            "total_nodes": len(graph.nodes),
            "total_edges": len(graph.edges),
            "by_type": type_counts,
            "cycle_count": len(cycle_nodes),
        },
        "unreachable": {
            "count": len(graph.unreachable),
        },
        "files_created": [
            "graph/dependency-graph.yaml",
            "graph/topological-order.yaml",
            "libraries.yaml",
        ],
    }

    ctx.output(single(item=output, semantic_key="graph", branch_id=branch_id))


# ============================================================================
# Filesystem-based graph building (offline, no API required)
# ============================================================================


def _scan_config_directory(
    base_dir: Path,
) -> list[tuple[Path, str, str, str | None, int]]:
    """Scan document directory for config files.

    Walks the directory structure created by 'document build':
    - local/<type>/<ref_name>.yaml for owned configs
    - <Library>/<BranchId>/<type>/<ref_name>.yaml for library configs

    Returns:
        List of (path, ref_name, config_type, library_name, branch_id)
    """
    configs: list[tuple[Path, str, str, str | None, int]] = []

    # Scan local configs: local/<type>/<ref_name>.yaml
    local_dir = base_dir / "local"
    if local_dir.exists():
        for type_dir in local_dir.iterdir():
            if type_dir.is_dir():
                config_type = type_dir.name
                for yaml_file in type_dir.glob("*.yaml"):
                    ref_name = yaml_file.stem
                    # Get branch_id from file content
                    try:
                        with open(yaml_file) as f:
                            data = yaml.safe_load(f)
                        branch_id = data.get("source_branch_id", 0)
                        configs.append((yaml_file, ref_name, config_type, None, branch_id))
                    except Exception:
                        pass  # Skip malformed files

    # Scan library configs: <LibraryName>/<BranchId>/<type>/<ref_name>.yaml
    for item in base_dir.iterdir():
        if item.is_dir() and item.name not in ("local", "graph"):
            lib_name = item.name
            for branch_dir in item.iterdir():
                if branch_dir.is_dir() and branch_dir.name.isdigit():
                    branch_id = int(branch_dir.name)
                    for type_dir in branch_dir.iterdir():
                        if type_dir.is_dir():
                            config_type = type_dir.name
                            for yaml_file in type_dir.glob("*.yaml"):
                                ref_name = yaml_file.stem
                                configs.append((yaml_file, ref_name, config_type, lib_name, branch_id))

    return configs


def _load_libraries_yaml(base_dir: Path) -> tuple[int, dict[str, int]]:
    """Load libraries.yaml and return (main_branch_id, library_branches)."""
    lib_path = base_dir / "libraries.yaml"
    if not lib_path.exists():
        raise ValidationError(
            f"libraries.yaml not found in {base_dir}",
            suggestions=["Run 'dxs source document build' first to create the config files"],
        )

    with open(lib_path) as f:
        data = yaml.safe_load(f)

    return data.get("branch_id", 0), data.get("libraries", {})


def _build_config_index_from_filesystem(
    configs: list[tuple[Path, str, str, str | None, int]],
) -> dict[str, tuple[str, int, str, bool]]:
    """Build config index from filesystem scan.

    Returns:
        Dict: ref_name_lower -> (config_type, config_id, app_ref_name, is_external)
    """
    index: dict[str, tuple[str, int, str, bool]] = {}

    for path, ref_name, config_type, lib_name, _branch_id in configs:
        try:
            with open(path) as f:
                data = yaml.safe_load(f)
            config_id = data.get("config_id", 0)
        except Exception:
            config_id = 0

        key = ref_name.lower()
        is_external = lib_name is not None
        app_ref = lib_name or ""

        # Prefer owned configs over external when there are duplicates
        existing = index.get(key)
        if existing is None:
            index[key] = (config_type, config_id, app_ref, is_external)
        elif not is_external and existing[3]:
            # Replace external with local
            index[key] = (config_type, config_id, app_ref, is_external)

    return index


def build_dependency_graph_from_filesystem(
    base_dir: Path,
    target: str | None = None,
    max_depth: int = 10,
    include_external: bool = True,
) -> DependencyGraph:
    """Build dependency graph from downloaded config files.

    Args:
        base_dir: Directory containing document build output
        target: Optional starting config (default: all shells)
        max_depth: Maximum traversal depth
        include_external: Whether to include library configs

    Returns:
        DependencyGraph with all discovered nodes and edges
    """
    _, _, _extract_all_references, _ = _get_explore_helpers()

    # Load library mappings
    main_branch_id, library_branches = _load_libraries_yaml(base_dir)

    # Load info.yaml for app name
    info_path = base_dir / "info.yaml"
    app_name = "Unknown"
    if info_path.exists():
        with open(info_path) as f:
            info = yaml.safe_load(f)
        app_name = info.get("app_name", "Unknown")

    graph = DependencyGraph(branch_id=main_branch_id, app_name=app_name, target=target)
    graph.library_branches = library_branches

    # Scan filesystem for configs
    _progress("  Scanning filesystem for configs...")
    configs = _scan_config_directory(base_dir)
    _progress(f"  Found {len(configs)} config files")

    # Build config index
    _progress("  Building configuration index...")
    config_index = _build_config_index_from_filesystem(configs)
    graph._full_index = config_index.copy()

    # Load all configs into memory for reference extraction
    _progress("  Loading config contents...")
    config_cache: dict[str, dict[str, Any]] = {}  # ref_lower -> raw_config
    config_metadata: dict[str, tuple[str, int, str | None, int]] = {}  # ref_lower -> (type, id, lib, branch)

    for path, ref_name, config_type, lib_name, branch_id in configs:
        try:
            with open(path) as f:
                data = yaml.safe_load(f)
            raw_config = data.get("raw_config", {})
            config_id = data.get("config_id", 0)
            key = ref_name.lower()
            config_cache[key] = raw_config
            config_metadata[key] = (config_type, config_id, lib_name, branch_id)
        except Exception:
            pass

    _progress(f"  Loaded {len(config_cache)} configs into memory")

    # DFS traversal
    visited: set[str] = set()
    in_stack: set[str] = set()

    def dfs(ref_name: str, depth: int) -> None:
        key = ref_name.lower()

        if depth > max_depth or key in visited:
            return

        if key in in_stack:
            if key in graph.nodes:
                graph.nodes[key].in_cycle = True
            return

        visited.add(key)
        in_stack.add(key)

        metadata = config_metadata.get(key)
        if not metadata:
            in_stack.discard(key)
            return

        config_type, config_id, lib_name, source_branch = metadata
        is_external = lib_name is not None

        if not include_external and is_external:
            in_stack.discard(key)
            return

        raw_config = config_cache.get(key)
        if raw_config is None:
            in_stack.discard(key)
            return

        # Create node
        label = raw_config.get("label") or raw_config.get("title") or ref_name
        node = GraphNode(
            reference_name=ref_name,
            config_type=config_type,
            config_id=config_id,
            branch_id=source_branch,
            application_ref_name=lib_name or "",
            is_external=is_external,
            label=label,
            depth=depth,
        )
        graph.add_node(node)

        # Extract references
        refs = _extract_all_references(raw_config, config_type, config_index)

        for ref_type, ref_list in refs.items():
            edge_type = ref_type.rstrip("s")
            for ref in ref_list:
                ref_metadata = config_metadata.get(ref.lower())
                if ref_metadata:
                    _, _, ref_lib, _ = ref_metadata
                    ref_is_external = ref_lib is not None
                    if not include_external and ref_is_external:
                        continue
                    graph.add_edge(ref_name, ref, edge_type)
                    dfs(ref, depth + 1)

        in_stack.discard(key)

    # Determine starting points
    if target:
        _progress(f"  Starting from target: {target}")
        roots = [target]
        dfs(target, 0)
    else:
        # Find all shells
        _progress("  Finding entry points (shells)...")
        roots = []
        for key, (config_type, _, _, _) in config_metadata.items():
            if config_type == "shell":
                roots.append(key)
                dfs(key, 0)
        _progress(f"  Found {len(roots)} shell(s)")

    _progress(f"  DFS complete: {len(graph.nodes)} nodes discovered")

    # Compute depths and unreachable
    compute_depths(graph, roots)
    graph.compute_unreachable()

    return graph


def build_graph_from_traces(
    base_dir: Path,
    target: str | None = None,
) -> tuple[DependencyGraph, dict[str, list[dict[str, str]]]]:
    """Build dependency graph from .trace.yaml files.

    This is faster than build_dependency_graph_from_filesystem() because it reads
    pre-computed trace files instead of re-extracting references from raw configs.

    Args:
        base_dir: Directory containing document build output with trace files
        target: Optional starting config (default: all shells)

    Returns:
        Tuple of (DependencyGraph, missing_references)
        - missing_references: dict mapping source config to list of unresolved refs
    """
    # Load library mappings
    main_branch_id, library_branches = _load_libraries_yaml(base_dir)

    # Load info.yaml for app name
    info_path = base_dir / "info.yaml"
    app_name = "Unknown"
    if info_path.exists():
        with open(info_path) as f:
            info = yaml.safe_load(f)
        app_name = info.get("app_name", "Unknown")

    graph = DependencyGraph(branch_id=main_branch_id, app_name=app_name, target=target)
    graph.library_branches = library_branches

    # Pass 1: Scan for config files and build nodes
    _progress("  Pass 1: Building nodes from config files...")
    configs = _scan_config_directory(base_dir)
    _progress(f"  Found {len(configs)} config files")

    # Build node index and create nodes
    node_index: dict[str, tuple[str, int, str | None, int, Path]] = {}  # ref_lower -> (type, id, lib, branch, path)

    for path, ref_name, config_type, lib_name, branch_id in configs:
        # Skip trace files
        if path.name.endswith(".trace.yaml"):
            continue

        key = ref_name.lower()
        try:
            with open(path) as f:
                data = yaml.safe_load(f)
            config_id = data.get("config_id", 0)
            raw_config = data.get("raw_config", {})
            label = raw_config.get("label") or raw_config.get("title") or ref_name
        except Exception:
            config_id = 0
            label = ref_name

        node_index[key] = (config_type, config_id, lib_name, branch_id, path)

        is_external = lib_name is not None
        node = GraphNode(
            reference_name=ref_name,
            config_type=config_type,
            config_id=config_id,
            branch_id=branch_id,
            application_ref_name=lib_name or "",
            is_external=is_external,
            label=label,
        )
        graph.add_node(node)

    _progress(f"  Created {len(graph.nodes)} nodes")

    # Store full index for unreachable detection
    graph._full_index = {k: (v[0], v[1], v[2] or "", v[2] is not None) for k, v in node_index.items()}

    # Pass 2: Read trace files and build edges
    _progress("  Pass 2: Building edges from trace files...")
    missing_references: dict[str, list[dict[str, str]]] = {}
    edges_created = 0
    edges_seen: set[tuple[str, str, str]] = set()  # (from, to, type) for deduplication
    self_refs_skipped = 0

    for path, _ref_name, _config_type, _lib_name, _branch_id in configs:
        # Only process trace files
        if not path.name.endswith(".trace.yaml"):
            continue

        try:
            with open(path) as f:
                trace_data = yaml.safe_load(f)
        except Exception:
            continue

        # Get the actual reference name from the trace file (not from path)
        source_ref_name = trace_data.get("reference_name", "")
        if not source_ref_name:
            continue

        references = trace_data.get("references", {})

        for ref_type, ref_list in references.items():
            # Skip non-edge reference types
            if ref_type in SKIP_REFERENCE_TYPES:
                continue

            # Get semantic edge type
            edge_type = EDGE_TYPE_MAP.get(ref_type)
            if edge_type is None:
                continue

            for ref_entry in ref_list:
                # Handle both dict format {name, library} and simple string
                if isinstance(ref_entry, dict):
                    target_name = ref_entry.get("name", "")
                else:
                    target_name = str(ref_entry)

                if not target_name:
                    continue

                target_key = target_name.lower()
                source_key = source_ref_name.lower()

                # Skip self-referential edges
                if source_key == target_key:
                    self_refs_skipped += 1
                    continue

                # Check if target exists
                if target_key in node_index:
                    # Deduplicate edges
                    edge_key = (source_key, target_key, edge_type)
                    if edge_key not in edges_seen:
                        edges_seen.add(edge_key)
                        graph.add_edge(source_ref_name, target_name, edge_type)
                        edges_created += 1
                else:
                    # Track missing reference
                    missing_references.setdefault(source_ref_name, []).append({
                        "name": target_name,
                        "type": edge_type,
                        "ref_type": ref_type,
                    })

    _progress(f"  Created {edges_created} unique edges (skipped {self_refs_skipped} self-references)")
    if missing_references:
        total_missing = sum(len(refs) for refs in missing_references.values())
        _progress(f"  Found {total_missing} missing references from {len(missing_references)} configs")

    # Pass 3: Determine roots and compute depths
    _progress("  Pass 3: Computing depths and detecting cycles...")
    if target:
        roots = [target.lower()]
    else:
        # Find all shells
        roots = [key for key, node in graph.nodes.items() if node.config_type == "shell"]
        _progress(f"  Found {len(roots)} shell(s) as entry points")

    compute_depths(graph, roots)
    graph.compute_unreachable()

    return graph, missing_references


@document.command("graph")
@click.option(
    "--input-dir", "-i",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=True,
    help="Directory containing document build output with trace files",
)
@click.option("--target", "-t", type=str, default=None, help="Starting config reference name")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing graph files")
@pass_context
def graph(
    ctx: DxsContext,
    input_dir: str,
    target: str | None,
    force: bool,
) -> None:
    """Build dependency graph from trace files.

    Reads .trace.yaml files from a previous 'document build' + 'explore trace --batch'
    and generates the dependency graph with semantic edge types.

    \b
    Requires:
        1. Run 'dxs source document build --branch <id>' to download configs
        2. Run 'dxs source explore trace --offline --batch <dir>' to generate traces

    \b
    Output:
        <input_dir>/graph/dependency-graph.yaml
        <input_dir>/graph/topological-order.yaml

    \b
    Examples:
        dxs source document graph -i ./exploration/MyApp/12345
        dxs source document graph -i ./docs --target my_hub
    """
    in_path = Path(input_dir)

    # Check if graph already exists
    graph_path = in_path / "graph" / "dependency-graph.yaml"
    if graph_path.exists() and not force:
        raise ValidationError(
            f"Graph already exists at {graph_path}. Use --force to overwrite.",
            code="DXS-DOC-003",
        )

    _progress("")
    _progress("=" * 60)
    _progress("DXS SOURCE DOCUMENT - Graph from Trace Files")
    _progress("=" * 60)
    _progress(f"  Input directory: {in_path.absolute()}")
    _progress("")

    # Build graph from trace files
    _progress("Building dependency graph from trace files...")
    dep_graph, missing_references = build_graph_from_traces(
        base_dir=in_path,
        target=target,
    )

    # Topological sort for cycle detection
    _progress("Performing topological sort...")
    sorted_order, cycle_nodes = topological_sort(dep_graph)

    if cycle_nodes:
        _progress(f"  Warning: {len(cycle_nodes)} configs form cycles")

    # Write output files
    _progress("Writing graph files...")
    _write_dependency_graph_with_missing(dep_graph, missing_references, cycle_nodes, in_path)
    _write_topological_order(dep_graph, sorted_order, cycle_nodes, in_path)

    # Count by type
    type_counts: dict[str, int] = {}
    for node in dep_graph.nodes.values():
        type_counts[node.config_type] = type_counts.get(node.config_type, 0) + 1

    # Count edges by type
    edge_type_counts: dict[str, int] = {}
    for edge in dep_graph.edges:
        edge_type_counts[edge.edge_type] = edge_type_counts.get(edge.edge_type, 0) + 1

    total_missing = sum(len(refs) for refs in missing_references.values())

    _progress("")
    _progress("=" * 60)
    _progress("COMPLETE")
    _progress("=" * 60)
    _progress(f"  Nodes: {len(dep_graph.nodes)}")
    _progress(f"  Edges: {len(dep_graph.edges)}")
    _progress(f"  Unreachable: {len(dep_graph.unreachable)}")
    _progress(f"  Cycles: {len(cycle_nodes)}")
    _progress(f"  Missing references: {total_missing}")
    _progress("")

    output = {
        "input_dir": str(in_path.absolute()),
        "app_name": dep_graph.app_name,
        "target": target,
        "graph_summary": {
            "total_nodes": len(dep_graph.nodes),
            "total_edges": len(dep_graph.edges),
            "nodes_by_type": type_counts,
            "edges_by_type": edge_type_counts,
            "cycle_count": len(cycle_nodes),
            "missing_references_count": total_missing,
        },
        "unreachable": {
            "count": len(dep_graph.unreachable),
        },
        "files_created": [
            "graph/dependency-graph.yaml",
            "graph/topological-order.yaml",
        ],
    }

    ctx.output(single(item=output, semantic_key="graph"))
