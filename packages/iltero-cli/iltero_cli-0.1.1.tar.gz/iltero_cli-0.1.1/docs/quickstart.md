# Quickstart Guide

Get up and running with Iltero CLI in 5 minutes!

## Prerequisites

- **Python 3.11+** - Check with `python --version`
- **Iltero account** - Sign up at [iltero.io](https://iltero.io)

## 1. Install

```bash
pip install iltero-cli
```

Verify installation:
```bash
iltero --version
```

## 2. Get Your API Token

1. Log in to [Iltero web UI](https://app.iltero.io)
2. Go to **Settings** → **API Tokens**
3. Click **Create Token** → Choose **Personal Token**
4. Copy the token (starts with `itk_u_`)

## 3. Authenticate

### Option A: System Keyring (Recommended)

```bash
iltero auth set-token
# Paste your token when prompted
```

### Option B: Environment Variable

```bash
export ILTERO_TOKEN=itk_u_your_token_here
```

Verify authentication:
```bash
iltero auth status
```

## 4. Install Scanners (Optional)

For local compliance scanning:

```bash
pip install checkov
```

Verify:
```bash
iltero scanner check
```

## 5. Your First Scan

```bash
# Scan local Terraform code
iltero scan static --path ./terraform

# Or scan current directory
iltero scan static --path .
```

## 6. Create a Workspace

```bash
# Create workspace
iltero workspace create \
  --name my-workspace \
  --description "My infrastructure"

# Set as default
iltero context set workspace my-workspace
```

## 7. Create a Stack

```bash
# Create stack
iltero stack create \
  --name my-stack \
  --workspace my-workspace \
  --environment production \
  --repo-url https://github.com/org/repo.git

# Scan and upload results
iltero scan static \
  --path ./terraform \
  --stack-id stk_abc123 \
  --upload
```

## Common Workflows

### Local Development

```bash
# Check scanners
iltero scanner check

# Scan infrastructure code
iltero scan static --path ./terraform

# View compliance violations
iltero compliance violations list --severity critical
```

### CI/CD Pipeline

```bash
# Create pipeline token
iltero token create --name "GitHub Actions" --type pipeline

# Add to CI/CD secrets as ILTERO_PIPELINE_TOKEN

# In your pipeline:
export ILTERO_TOKEN=$PIPELINE_TOKEN
iltero scan static --path . --fail-on critical
```

### Multi-Environment Setup

```bash
# Create workspaces
iltero workspace create --name production
iltero workspace create --name staging
iltero workspace create --name development

# Set context for daily work
iltero context set workspace development
iltero stack list  # Uses development workspace
```

## Configuration

The CLI can be configured via:

### Environment Variables

Key environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `ILTERO_TOKEN` | API authentication token | None (required) |
| `ILTERO_API_URL` | Backend API URL | `https://api.iltero.io` |
| `ILTERO_OUTPUT_FORMAT` | Output format | `table` |
| `ILTERO_DEBUG` | Enable debug logging | `false` |
| `ILTERO_NO_COLOR` | Disable colored output | `false` |

### Config File

Create `~/.iltero/config.yaml`:

```yaml
api_url: https://api.iltero.io
output_format: table
debug: false
```

## Getting Help

```bash
# General help
iltero --help

# Command-specific help
iltero scan --help
iltero workspace create --help
```

## Next Steps

- **[Installation Guide](installation.md)** - Detailed installation for all platforms
- **[Configuration Guide](configuration.md)** - Advanced configuration options
- **[Command Reference](commands/index.md)** - Complete command documentation
- **[CI/CD Integration](ci-cd/README.md)** - Set up automated scanning
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

## Need Help?

- Check `iltero auth status` to verify authentication
- Enable debug mode: `iltero --debug [command]`
- Review logs at `~/.iltero/logs/`
- Visit [documentation](README.md)
- Report issues on [GitHub](https://github.com/iltero/iltero-cli/issues)

# Format code
black iltero tests

# Lint code
ruff check iltero tests

# Type checking
mypy iltero
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

## Phase 1 Checklist

- [x] CLI can be installed via `pip install -e .`
- [x] `iltero --version` works
- [x] `iltero --help` shows all command groups
- [x] `iltero auth set-token` stores token in keyring
- [x] `iltero auth show-token` displays masked token
- [x] `iltero auth status` shows authentication state
- [x] Token retrieved from `ILTERO_TOKEN` env var in CI/CD mode
- [x] All backend settings configurable via environment variables
- [ ] OpenAPI client generated from backend spec (Phase 2)
- [x] Project structure matches specification
- [x] Unit tests for core modules

## Next Steps (Phase 2)

1. Generate OpenAPI client from backend
2. Implement workspace commands
3. Implement environment commands
4. Implement stack commands
5. Add output formatters (JSON, YAML)
6. Implement context management
