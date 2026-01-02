# Configuration Guide

Complete guide to configuring the Iltero CLI.

## Table of Contents

- [Configuration Methods](#configuration-methods)
- [Environment Variables](#environment-variables)
- [Configuration File](#configuration-file)
- [Precedence Order](#precedence-order)
- [Authentication Configuration](#authentication-configuration)
- [Backend Configuration](#backend-configuration)
- [Scanner Configuration](#scanner-configuration)
- [Output Configuration](#output-configuration)
- [Context Configuration](#context-configuration)
- [Advanced Configuration](#advanced-configuration)

## Configuration Methods

The Iltero CLI can be configured in three ways:

1. **Command-line flags** - Temporary, one-time overrides
2. **Environment variables** - Session or system-wide settings
3. **Configuration file** - Persistent user preferences

## Environment Variables

All environment variables are prefixed with `ILTERO_`.

### Authentication

| Variable | Description | Example | Default |
|----------|-------------|---------|---------|
| `ILTERO_TOKEN` | API authentication token | `itk_u_abc...` | None (required) |

### Backend

| Variable | Description | Example | Default |
|----------|-------------|---------|---------|
| `ILTERO_API_URL` | Backend API URL | `https://api.iltero.io` | `https://api.iltero.io` |
| `ILTERO_REQUEST_TIMEOUT` | HTTP request timeout (seconds) | `30` | `30` |
| `ILTERO_VERIFY_SSL` | Verify SSL certificates | `true`/`false` | `true` |

### CLI Behavior

| Variable | Description | Example | Default |
|----------|-------------|---------|---------|
| `ILTERO_OUTPUT_FORMAT` | Default output format | `table`, `json`, `yaml` | `table` |
| `ILTERO_DEBUG` | Enable debug logging | `true`/`false` | `false` |
| `ILTERO_NO_COLOR` | Disable colored output | `true`/`false` | `false` |
| `ILTERO_LOG_LEVEL` | Logging level | `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO` |
| `ILTERO_LOG_FILE` | Log file path | `~/.iltero/logs/cli.log` | None |

### Scanner Settings

| Variable | Description | Example | Default |
|----------|-------------|---------|---------|
| `ILTERO_SCAN_TIMEOUT` | Scanner execution timeout (seconds) | `300` | `300` |
| `ILTERO_CHECKOV_PATH` | Path to checkov binary | `/usr/local/bin/checkov` | Auto-detect |
| `ILTERO_OPA_PATH` | Path to OPA binary | `/usr/local/bin/opa` | Auto-detect |
| `ILTERO_SCANNER_CHECKOV_ARGS` | Additional checkov arguments | `--quiet,--compact` | None |
| `ILTERO_SCANNER_OPA_ARGS` | Additional OPA arguments | `--format pretty` | None |

### Context

| Variable | Description | Example | Default |
|----------|-------------|---------|---------|
| `ILTERO_DEFAULT_ORG` | Default organization | `my-org` | None |
| `ILTERO_DEFAULT_WORKSPACE` | Default workspace | `production-infra` | None |
| `ILTERO_DEFAULT_ENVIRONMENT` | Default environment | `production` | None |

### Setting Environment Variables

#### Bash/Zsh

```bash
# Add to ~/.bashrc or ~/.zshrc
export ILTERO_TOKEN=itk_u_your_token_here
export ILTERO_OUTPUT_FORMAT=json
export ILTERO_DEBUG=false
```

#### Fish

```fish
# Add to ~/.config/fish/config.fish
set -gx ILTERO_TOKEN itk_u_your_token_here
set -gx ILTERO_OUTPUT_FORMAT json
```

#### Windows PowerShell

```powershell
# Add to $PROFILE
$env:ILTERO_TOKEN = "itk_u_your_token_here"
$env:ILTERO_OUTPUT_FORMAT = "json"
```

#### Windows Command Prompt

```cmd
# Set temporarily
set ILTERO_TOKEN=itk_u_your_token_here

# Set permanently
setx ILTERO_TOKEN itk_u_your_token_here
```

## Configuration File

The CLI looks for a configuration file at `~/.iltero/config.yaml`.

### Creating the Config File

```bash
# Create directory
mkdir -p ~/.iltero

# Create config file
cat > ~/.iltero/config.yaml << 'EOF'
# API Configuration
api_url: https://api.iltero.io
request_timeout: 30
verify_ssl: true

# CLI Behavior
output_format: table  # table, json, yaml
debug: false
no_color: false
log_level: INFO

# Scanner Settings
scan_timeout: 300
scanner_checkov_args:
  - --quiet
  - --compact
scanner_opa_args:
  - --format
  - pretty

# Default Context
default_org: my-org
default_workspace: production-infra
default_environment: production

# Advanced Settings
cache_enabled: true
cache_dir: ~/.iltero/cache
cache_ttl: 3600  # seconds
EOF
```

### Configuration File Schema

```yaml
# ============================================
# API Configuration
# ============================================
api_url: https://api.iltero.io
request_timeout: 30  # seconds
verify_ssl: true
retry_attempts: 3
retry_backoff: 2  # exponential backoff multiplier

# ============================================
# Authentication
# ============================================
# Note: Token should be in keyring or env var, not config file
token_storage: keyring  # keyring or file (not recommended)

# ============================================
# CLI Behavior
# ============================================
output_format: table  # table, json, yaml
debug: false
no_color: false
log_level: INFO  # DEBUG, INFO, WARNING, ERROR
log_file: ~/.iltero/logs/cli.log
interactive: true  # prompt for confirmations

# ============================================
# Scanner Settings
# ============================================
scan_timeout: 300  # seconds
scanner_checkov_path: /usr/local/bin/checkov
scanner_opa_path: /usr/local/bin/opa
scanner_checkov_args:
  - --quiet
  - --compact
  - --framework terraform
scanner_opa_args:
  - --format
  - pretty

# ============================================
# Default Context
# ============================================
default_org: my-org
default_workspace: production-infra
default_environment: production

# ============================================
# Output Formatting
# ============================================
table_style: rounded  # simple, rounded, grid, minimal
max_column_width: 80
truncate_long_text: true
show_timestamps: true
timestamp_format: "%Y-%m-%d %H:%M:%S"

# ============================================
# Caching
# ============================================
cache_enabled: true
cache_dir: ~/.iltero/cache
cache_ttl: 3600  # seconds
cache_max_size: 100  # MB

# ============================================
# Advanced Settings
# ============================================
parallel_scans: true
max_workers: 4
progress_bar: true
telemetry_enabled: true

# ============================================
# Cloud Provider Defaults
# ============================================
aws:
  default_region: us-east-1
  profile: default
azure:
  default_location: eastus
  subscription_id: ""
gcp:
  default_region: us-central1
  project_id: ""
```

## Precedence Order

Configuration is loaded in this order (highest to lowest priority):

1. **Command-line flags** - Highest priority
   ```bash
   iltero workspace list --output json
   ```

2. **Environment variables** - Override config file
   ```bash
   export ILTERO_OUTPUT_FORMAT=json
   iltero workspace list
   ```

3. **Configuration file** - User defaults
   ```yaml
   # ~/.iltero/config.yaml
   output_format: json
   ```

4. **Built-in defaults** - Lowest priority

### Example

```bash
# Config file has: output_format: table
# Environment has: ILTERO_OUTPUT_FORMAT=json
# Command has: --output yaml

iltero workspace list --output yaml
# Result: Uses YAML (command-line wins)
```

## Authentication Configuration

### Interactive Mode (Keyring Storage)

Best for local development:

```bash
# Store token in system keyring
iltero auth set-token
# Enter token when prompted
```

**Supported keyrings:**
- macOS: Keychain
- Windows: Credential Manager
- Linux: Secret Service (GNOME Keyring, KWallet)

### Environment Variable Mode

Best for CI/CD:

```bash
export ILTERO_TOKEN=itk_p_your_pipeline_token
```

### File Storage (Not Recommended)

Only use if keyring is unavailable:

```yaml
# ~/.iltero/config.yaml
token_storage: file
```

This stores token at `~/.iltero/token` (chmod 600).

⚠️ **Security Warning**: File storage is less secure than keyring storage.

## Backend Configuration

### Using Production Backend

```bash
# Default - no configuration needed
iltero auth status
# Uses: https://api.iltero.io
```

### Using Staging Backend

```bash
export ILTERO_API_URL=https://staging.iltero.com
iltero auth status
```

### Using Self-Hosted Backend

```bash
export ILTERO_API_URL=https://iltero.company.internal
iltero auth status
```

### SSL Configuration

```bash
# Disable SSL verification (not recommended for production)
export ILTERO_VERIFY_SSL=false

# Or in config file:
# verify_ssl: false
```

### Timeout Configuration

```bash
# Increase timeout for slow connections
export ILTERO_REQUEST_TIMEOUT=60

# Or in config file:
# request_timeout: 60
```

## Scanner Configuration

### Scanner Paths

By default, the CLI auto-detects scanners. To specify custom paths:

```yaml
# ~/.iltero/config.yaml
scanner_checkov_path: /custom/path/to/checkov
scanner_opa_path: /custom/path/to/opa
```

Or via environment:

```bash
export ILTERO_CHECKOV_PATH=/custom/path/to/checkov
export ILTERO_OPA_PATH=/custom/path/to/opa
```

### Scanner Arguments

Pass additional arguments to scanners:

```yaml
# ~/.iltero/config.yaml
scanner_checkov_args:
  - --quiet
  - --compact
  - --framework
  - terraform
  - --skip-check
  - CKV_AWS_1

scanner_opa_args:
  - --format
  - pretty
  - --bundle
  - /path/to/bundle
```

Or via environment (comma-separated):

```bash
export ILTERO_SCANNER_CHECKOV_ARGS="--quiet,--compact,--framework,terraform"
```

### Scan Timeout

```bash
# Increase for large repositories
export ILTERO_SCAN_TIMEOUT=600  # 10 minutes
```

## Output Configuration

### Default Format

```bash
# Set default output format
export ILTERO_OUTPUT_FORMAT=json

# Or in config:
# output_format: json
```

### Table Styling

```yaml
# ~/.iltero/config.yaml
table_style: rounded  # simple, rounded, grid, minimal
max_column_width: 80
truncate_long_text: true
```

### Colored Output

```bash
# Disable colors (useful for CI/CD logs)
export ILTERO_NO_COLOR=true

# Or in config:
# no_color: true
```

### Timestamp Format

```yaml
# ~/.iltero/config.yaml
show_timestamps: true
timestamp_format: "%Y-%m-%d %H:%M:%S"  # Or "%d/%m/%Y %I:%M %p"
```

## Context Configuration

### Setting Defaults

Avoid typing `--workspace` and `--environment` repeatedly:

```yaml
# ~/.iltero/config.yaml
default_org: my-org
default_workspace: production-infra
default_environment: production
```

Or via environment:

```bash
export ILTERO_DEFAULT_ORG=my-org
export ILTERO_DEFAULT_WORKSPACE=production-infra
export ILTERO_DEFAULT_ENVIRONMENT=production
```

### Using Context

```bash
# With default workspace set
iltero stack list  # Uses production-infra workspace

# Override temporarily
iltero stack list --workspace dev-infra
```

### Multiple Contexts

Create different config files for different contexts:

```bash
# Production config
export ILTERO_CONFIG_FILE=~/.iltero/prod-config.yaml
iltero workspace list

# Staging config
export ILTERO_CONFIG_FILE=~/.iltero/staging-config.yaml
iltero workspace list
```

## Advanced Configuration

### Caching

Enable caching to improve performance:

```yaml
# ~/.iltero/config.yaml
cache_enabled: true
cache_dir: ~/.iltero/cache
cache_ttl: 3600  # 1 hour
cache_max_size: 100  # MB
```

Clear cache:

```bash
rm -rf ~/.iltero/cache
```

### Logging

Configure detailed logging:

```yaml
# ~/.iltero/config.yaml
debug: true
log_level: DEBUG
log_file: ~/.iltero/logs/cli.log
```

View logs:

```bash
tail -f ~/.iltero/logs/cli.log
```

### Parallel Execution

Configure parallel scanning:

```yaml
# ~/.iltero/config.yaml
parallel_scans: true
max_workers: 4
```

### Progress Indicators

```yaml
# ~/.iltero/config.yaml
progress_bar: true
interactive: true
```

### Telemetry

```yaml
# ~/.iltero/config.yaml
telemetry_enabled: false  # Opt-out of anonymous usage stats
```

## Configuration Examples

### Developer Workstation

```yaml
# ~/.iltero/config.yaml
api_url: https://api.iltero.io
output_format: table
debug: false
interactive: true
default_workspace: my-workspace
cache_enabled: true
```

### CI/CD Pipeline

```bash
# .gitlab-ci.yml or .github/workflows/main.yml
export ILTERO_TOKEN=$PIPELINE_TOKEN
export ILTERO_OUTPUT_FORMAT=json
export ILTERO_NO_COLOR=true
export ILTERO_DEBUG=false
export ILTERO_INTERACTIVE=false
```

### Multi-Environment Setup

```bash
# Production
cat > ~/.iltero/prod-config.yaml << EOF
api_url: https://api.iltero.io
default_workspace: production-infra
default_environment: production
EOF

# Staging
cat > ~/.iltero/staging-config.yaml << EOF
api_url: https://staging.iltero.com
default_workspace: staging-infra
default_environment: staging
EOF

# Usage
export ILTERO_CONFIG_FILE=~/.iltero/prod-config.yaml
iltero workspace list
```

## Validation

Validate your configuration:

```bash
iltero config validate

# Output:
# ✓ Configuration is valid
# ✓ API URL is reachable
# ✓ Token is valid
# ✓ Scanners are available
```

Show current configuration:

```bash
iltero config show

# Output shows merged configuration from all sources
```

## Troubleshooting

### Configuration Not Loading

```bash
# Check which config file is being used
iltero --debug config show

# Verify file exists and is readable
ls -la ~/.iltero/config.yaml
```

### Environment Variables Not Working

```bash
# Verify environment variable is set
echo $ILTERO_TOKEN

# Check if it's being recognized
iltero --debug auth status
```

### Scanner Not Found

```bash
# Check scanner paths
iltero scanner check --debug

# Manually specify path
export ILTERO_CHECKOV_PATH=/usr/local/bin/checkov
```

## Security Best Practices

1. **Never commit tokens** to version control
2. **Use keyring storage** instead of file storage
3. **Use pipeline tokens** in CI/CD, not personal tokens
4. **Set appropriate file permissions** on config files:
   ```bash
   chmod 600 ~/.iltero/config.yaml
   ```
5. **Rotate tokens regularly**
6. **Use environment-specific tokens**

## See Also

- [Getting Started Guide](GETTING_STARTED.md)
- [Command Reference](COMMAND_REFERENCE.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
