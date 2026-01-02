# Getting Started with Iltero CLI

Welcome to Iltero CLI! This guide will help you get up and running quickly.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Initial Setup](#initial-setup)
- [Basic Usage](#basic-usage)
- [Common Workflows](#common-workflows)
- [Next Steps](#next-steps)

## Prerequisites

Before installing Iltero CLI, ensure you have:

- **Python 3.11 or higher** - Check with `python --version`
- **pip** - Python package installer (usually included with Python)
- **Git** (optional) - For installing from source
- **Iltero account** - Sign up at [iltero.io](https://iltero.io)
- **API token** - Generate from the Iltero web UI

### Scanner Prerequisites (Optional)

For local compliance scanning, install these scanners:

```bash
# Checkov (Infrastructure as Code scanner)
pip install checkov

# OPA (Open Policy Agent)
brew install opa  # macOS
# or download from: https://www.openpolicyagent.org/docs/latest/#running-opa
```

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install iltero-cli
```

### Option 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/iltero/iltero-cli.git
cd iltero-cli

# Install in editable mode
pip install -e .
```

### Option 3: Using a Virtual Environment (Recommended for Development)

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the CLI
pip install iltero-cli
```

### Verify Installation

```bash
iltero --version
# Output: iltero version X.X.X

iltero --help
# Shows all available commands
```

## Initial Setup

### 1. Get Your API Token

1. Log in to the [Iltero web UI](https://app.iltero.io)
2. Navigate to **Settings** → **API Tokens**
3. Click **Create Token**
4. Choose token type:
   - **Personal Token** (`itk_u_*`) - For your personal use
   - **Pipeline Token** (`itk_p_*`) - For CI/CD pipelines
   - **Service Token** (`itk_s_*`) - For automation/services
5. Copy the token (you won't see it again!)

### 2. Configure Authentication

#### Interactive Mode (Recommended for Local Development)

Store your token securely in your system keyring:

```bash
iltero auth set-token
# Enter your token when prompted
# Token will be stored in macOS Keychain, Windows Credential Manager, etc.
```

#### Environment Variable (Recommended for CI/CD)

Set the token as an environment variable:

```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export ILTERO_TOKEN=itk_u_your_token_here

# Or for one-time use
ILTERO_TOKEN=itk_u_your_token_here iltero auth status
```

### 3. Verify Authentication

```bash
iltero auth status
# Output:
# ✓ Authenticated as: john.doe@company.com
# Token Type: Personal Token
# API URL: https://api.iltero.io
```

### 4. Configure Backend URL (Optional)

By default, the CLI connects to `https://api.iltero.io`. To use a different backend:

```bash
# Using environment variable
export ILTERO_API_URL=https://staging.iltero.com

# Or create config file at ~/.iltero/config.yaml
mkdir -p ~/.iltero
cat > ~/.iltero/config.yaml << EOF
api_url: https://staging.iltero.com
output_format: table
debug: false
EOF
```

## Basic Usage

### Understanding the Command Structure

All Iltero CLI commands follow this pattern:

```
iltero [COMMAND_GROUP] [SUBCOMMAND] [OPTIONS] [ARGUMENTS]
```

For example:
```bash
iltero workspace list --output json
│      │         │     └─ Option
│      │         └─ Subcommand
│      └─ Command group
└─ CLI name
```

### Getting Help

```bash
# General help
iltero --help

# Help for a command group
iltero workspace --help

# Help for a specific command
iltero workspace create --help
```

### Common Global Options

These options work with most commands:

```bash
--output FORMAT    # Output format: table, json, yaml (default: table)
--debug            # Enable debug logging
--no-color         # Disable colored output
--help             # Show help message
```

## Common Workflows

### Workflow 1: Managing Workspaces

```bash
# List all workspaces
iltero workspace list

# Create a new workspace
iltero workspace create --name my-workspace --description "My infrastructure"

# Show workspace details
iltero workspace get my-workspace

# Set as default workspace
iltero context set workspace my-workspace

# List stacks in workspace
iltero stack list
```

### Workflow 2: Running Compliance Scans

```bash
# Check if scanners are installed
iltero scanner check

# Run a static scan on local Terraform code
iltero scan static --path ./terraform --scanner checkov

# Run scan and upload results to backend
iltero scan static --path ./terraform --stack-id stk_abc123 --upload

# View scan results
iltero scan results show --scan-id scn_xyz789

# Export scan results
iltero scan results export --scan-id scn_xyz789 --format sarif > results.sarif
```

### Workflow 3: Managing Stacks

```bash
# Create a stack
iltero stack create \
  --name production-app \
  --workspace my-workspace \
  --environment production \
  --repo-url https://github.com/org/repo.git \
  --branch main

# List stacks
iltero stack list --workspace my-workspace

# Get stack details
iltero stack get production-app

# Update stack variables
iltero stack variables set --stack-id stk_abc123 --key region --value us-east-1

# Trigger stack validation
iltero stack validate --stack-id stk_abc123
```

### Workflow 4: CI/CD Integration

```bash
# In your CI/CD pipeline (e.g., GitHub Actions, GitLab CI)

# 1. Install CLI
pip install iltero-cli

# 2. Authenticate (use pipeline token)
export ILTERO_TOKEN=${{ secrets.ILTERO_PIPELINE_TOKEN }}

# 3. Run pre-plan validation
iltero scan static --path . --format json > scan-results.json

# 4. Check for critical violations
if [ $(jq '.violations | map(select(.severity == "CRITICAL")) | length' scan-results.json) -gt 0 ]; then
  echo "Critical violations found!"
  exit 1
fi

# 5. Plan phase evaluation
iltero stack plan --stack-id stk_abc123 --evaluate

# 6. Apply (if approved)
iltero stack apply --stack-id stk_abc123
```

### Workflow 5: Viewing Compliance Status

```bash
# List all violations
iltero compliance violations list --severity critical

# Get violation details
iltero compliance violations get vio_xyz789

# Mark violation as remediated
iltero compliance violations remediate vio_xyz789 --note "Applied fix in PR #123"

# View compliance dashboard
iltero compliance dashboard --workspace my-workspace
```

### Workflow 6: Working with Contexts

Contexts help you avoid typing `--workspace`, `--environment` repeatedly:

```bash
# Set default context
iltero context set workspace my-workspace
iltero context set environment production

# View current context
iltero context show

# Now commands use context automatically
iltero stack list  # Lists stacks in my-workspace

# Override context temporarily
iltero stack list --workspace different-workspace

# Clear context
iltero context clear
```

## Configuration Options

### Environment Variables

All configuration can be set via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `ILTERO_TOKEN` | API authentication token | None (required) |
| `ILTERO_API_URL` | Backend API URL | `https://api.iltero.io` |
| `ILTERO_OUTPUT_FORMAT` | Default output format | `table` |
| `ILTERO_DEBUG` | Enable debug logging | `false` |
| `ILTERO_NO_COLOR` | Disable colored output | `false` |
| `ILTERO_REQUEST_TIMEOUT` | HTTP timeout (seconds) | `30` |
| `ILTERO_SCAN_TIMEOUT` | Scanner timeout (seconds) | `300` |
| `ILTERO_DEFAULT_ORG` | Default organization | None |
| `ILTERO_DEFAULT_WORKSPACE` | Default workspace | None |
| `ILTERO_DEFAULT_ENVIRONMENT` | Default environment | None |

### Config File

Create `~/.iltero/config.yaml`:

```yaml
# API Configuration
api_url: https://api.iltero.io
request_timeout: 30

# CLI Behavior
output_format: table  # table, json, yaml
debug: false
no_color: false

# Scanner Settings
scan_timeout: 300
scanner_checkov_args:
  - --quiet
  - --compact

# Default Context
default_org: my-org
default_workspace: my-workspace
default_environment: production
```

### Precedence Order

Configuration is loaded in this order (highest to lowest priority):

1. **Command-line flags** - `--output json`
2. **Environment variables** - `ILTERO_OUTPUT_FORMAT=json`
3. **Config file** - `~/.iltero/config.yaml`
4. **Defaults** - Built-in defaults

## Next Steps

Now that you're set up, explore these resources:

- **[Command Reference](COMMAND_REFERENCE.md)** - Detailed documentation for all commands
- **[Configuration Guide](CONFIGURATION.md)** - Advanced configuration options
- **[CI/CD Integration Guide](CICD_INTEGRATION.md)** - Use Iltero in your pipelines
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Common issues and solutions
- **[API Examples](API_EXAMPLES.md)** - Integration with backend API

### Learn More

- Browse [example configurations](examples/)
- Read about [scanner integration](SCANNER_INTEGRATION.md)
- Check out [best practices](BEST_PRACTICES.md)
- Join our [community](https://community.iltero.io)

## Getting Help

If you run into issues:

1. Check `iltero auth status` to verify authentication
2. Enable debug mode: `iltero --debug [command]`
3. Review logs at `~/.iltero/logs/`
4. Search [existing issues](https://github.com/iltero/iltero-cli/issues)
5. Create a [new issue](https://github.com/iltero/iltero-cli/issues/new)

**Need immediate help?**
- Documentation: https://docs.iltero.io
- Support: support@iltero.io
- Community: https://community.iltero.io
