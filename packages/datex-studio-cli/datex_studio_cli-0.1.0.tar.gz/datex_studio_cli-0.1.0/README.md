# Datex Studio CLI (`dxs`)

Command-line interface for Datex Studio low-code platform, designed for LLM-based AI agents.

## Installation

```bash
# Using uv
uv pip install datex-studio-cli

# Using pip
pip install datex-studio-cli
```

## Quick Start

```bash
# Authenticate with Azure Entra
dxs auth login

# View commit history
dxs source log --repo 10

# View configuration history
dxs source history userGrid --branch 100

# View current locks
dxs source locks --repo 10
```

## Output Formats

The CLI supports multiple output formats optimized for LLM consumption:

```bash
# YAML (default)
dxs source log --repo 10

# JSON
dxs source log --repo 10 --output json

# CSV
dxs source log --repo 10 --output csv
```

## Configuration

Configuration is stored in `~/.datex/config.yaml`. You can also use environment variables:

```bash
# Set via environment
export DXS_API_BASE_URL=https://api.datex.io
export DXS_DEFAULT_BRANCH=100
export DXS_DEFAULT_REPO=10

# Set via CLI
dxs config set api_base_url https://api.datex.io
dxs config set default_branch 100
dxs config set default_repo 10

# View configuration
dxs config list
```

## Commands

### Authentication

- `dxs auth login` - Authenticate with Azure Entra
- `dxs auth logout` - Clear stored credentials
- `dxs auth status` - Show authentication status

### Configuration

- `dxs config get <key>` - Get a configuration value
- `dxs config set <key> <value>` - Set a configuration value
- `dxs config list` - List all configuration values

### Source Control

- `dxs source log` - Show commit history
- `dxs source history <ref>` - Show configuration version history
- `dxs source diff` - Show pending changes (draft vs last commit)
- `dxs source changes` - Show pending changes in detail
- `dxs source locks` - Show current lock status
- `dxs source deps` - Show configuration dependencies
- `dxs source compare` - Compare two branches

### Exploration

- `dxs source explore info` - Show application overview
- `dxs source explore configs` - List all configurations
- `dxs source explore config <ref>` - View a specific configuration
- `dxs source explore summary <ref>` - Show structural summary
- `dxs source explore trace <ref>` - Show configuration dependencies

### Branch & Repository Management

- `dxs source branch list` - List branches
- `dxs source branch show <id>` - Show branch details
- `dxs source repo list` - List repositories
- `dxs source repo show <id>` - Show repository details

### Integrations

- `dxs devops workitem <id>` - Get Azure DevOps work item
- `dxs crm case <id>` - Get Dynamics CRM case
- `dxs organization list` - List organizations
- `dxs marketplace list` - List marketplace applications
- `dxs api <method> <url>` - Make raw API requests

## Development

```bash
# Clone and install
git clone https://github.com/datex/datex-studio-cli.git
cd datex-studio-cli
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Run tests
pytest

# Lint and format
ruff check .
ruff format .

# Type check
mypy src/dxs
```

## License

MIT
