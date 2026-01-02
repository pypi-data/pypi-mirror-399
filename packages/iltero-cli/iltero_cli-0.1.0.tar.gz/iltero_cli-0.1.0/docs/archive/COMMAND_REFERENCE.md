# Command Reference

Complete reference for all Iltero CLI commands.

## Table of Contents

- [Global Options](#global-options)
- [Authentication Commands](#authentication-commands)
- [Token Commands](#token-commands)
- [Workspace Commands](#workspace-commands)
- [Environment Commands](#environment-commands)
- [Stack Commands](#stack-commands)
- [Scan Commands](#scan-commands)
- [Scanner Commands](#scanner-commands)
- [Compliance Commands](#compliance-commands)
- [Context Commands](#context-commands)
- [Repository Commands](#repository-commands)
- [Bundles Commands](#bundles-commands)
- [Registry Commands](#registry-commands)
- [Organization Commands](#organization-commands)
- [User Commands](#user-commands)

## Global Options

These options are available for all commands:

```bash
--output FORMAT     # Output format: table, json, yaml (default: table)
--debug             # Enable debug logging
--no-color          # Disable colored output
--help              # Show help message
--version           # Show CLI version
```

## Authentication Commands

### `iltero auth`

Manage authentication and API tokens.

#### `iltero auth set-token`

Store an API token in the system keyring.

```bash
iltero auth set-token
# Prompts for token input (hidden)
```

**Interactive prompt:**
```
Enter your Iltero API token: [hidden input]
✓ Token stored successfully in system keyring
```

#### `iltero auth show-token`

Display the stored API token.

```bash
# Show masked token (default)
iltero auth show-token
# Output: Token: itk_u_abc***xyz

# Show full token (use with caution)
iltero auth show-token --reveal
# Output: Token: itk_u_abcdefghijklmnopqrstuvwxyz
```

**Options:**
- `--reveal` - Show the full token instead of masked version

#### `iltero auth status`

Check authentication status and verify connectivity.

```bash
iltero auth status

# Output:
# ✓ Authenticated as: john.doe@company.com
# Token Type: Personal Token (itk_u_*)
# API URL: https://api.iltero.io
# Status: Connected
```

**JSON output:**
```bash
iltero auth status --output json
```

```json
{
  "authenticated": true,
  "user_email": "john.doe@company.com",
  "token_type": "personal",
  "token_prefix": "itk_u",
  "api_url": "https://api.iltero.io",
  "status": "connected"
}
```

#### `iltero auth clear-token`

Remove the stored token from the keyring.

```bash
iltero auth clear-token
# Output: ✓ Token cleared successfully
```

#### `iltero auth whoami`

Display information about the authenticated user.

```bash
iltero auth whoami

# Output:
# User: john.doe@company.com
# Name: John Doe
# Organization: ACME Corp
# Role: Developer
```

## Token Commands

### `iltero token`

Manage API tokens (create, list, revoke).

#### `iltero token list`

List all tokens for the authenticated user.

```bash
iltero token list

# Table output:
# ID          Name              Type      Created              Last Used            Status
# ────────────────────────────────────────────────────────────────────────────────────────
# tok_abc123  My Personal       Personal  2024-01-15 10:30:00  2024-12-04 14:20:00  Active
# tok_def456  CI/CD Pipeline    Pipeline  2024-02-01 08:15:00  2024-12-04 12:00:00  Active
```

**Options:**
- `--type TYPE` - Filter by token type: `personal`, `pipeline`, `service`, `registry`
- `--status STATUS` - Filter by status: `active`, `revoked`

#### `iltero token create`

Create a new API token.

```bash
# Create personal token
iltero token create --name "My Development Token" --type personal

# Create pipeline token
iltero token create --name "GitHub Actions" --type pipeline --expires-in 90

# Create service token
iltero token create --name "Monitoring Service" --type service
```

**Options:**
- `--name NAME` (required) - Token name
- `--type TYPE` (required) - Token type: `personal`, `pipeline`, `service`, `registry`
- `--expires-in DAYS` - Token expiration in days (optional)
- `--scopes SCOPES` - Comma-separated scopes (optional)

**Output:**
```
✓ Token created successfully

Token ID: tok_xyz789
Token: itk_p_abcdefghijklmnopqrstuvwxyz1234567890

⚠️  Save this token now - you won't see it again!
```

#### `iltero token revoke`

Revoke an API token.

```bash
iltero token revoke tok_abc123

# With confirmation
iltero token revoke tok_abc123 --confirm
```

**Options:**
- `--confirm` - Skip confirmation prompt

## Workspace Commands

### `iltero workspace`

Manage workspaces (isolated environments for stacks).

#### `iltero workspace list`

List all workspaces.

```bash
iltero workspace list

# With filters
iltero workspace list --org my-org --status active
```

**Options:**
- `--org ORG` - Filter by organization
- `--status STATUS` - Filter by status: `active`, `archived`

#### `iltero workspace create`

Create a new workspace.

```bash
iltero workspace create \
  --name production-infra \
  --description "Production infrastructure workspace" \
  --org my-org
```

**Options:**
- `--name NAME` (required) - Workspace name
- `--description DESC` - Workspace description
- `--org ORG` - Organization (uses default if not specified)

#### `iltero workspace get`

Get workspace details.

```bash
iltero workspace get production-infra

# By ID
iltero workspace get wsp_abc123
```

#### `iltero workspace update`

Update workspace settings.

```bash
iltero workspace update production-infra \
  --description "Updated description" \
  --tags "environment:prod,team:platform"
```

**Options:**
- `--description DESC` - New description
- `--tags TAGS` - Comma-separated tags

#### `iltero workspace delete`

Delete a workspace.

```bash
iltero workspace delete production-infra

# Force delete without confirmation
iltero workspace delete production-infra --force
```

**Options:**
- `--force` - Skip confirmation prompt

## Environment Commands

### `iltero environment`

Manage environments within workspaces.

#### `iltero environment list`

List environments in a workspace.

```bash
iltero environment list --workspace production-infra
```

#### `iltero environment create`

Create a new environment.

```bash
iltero environment create \
  --name production \
  --workspace production-infra \
  --cloud aws \
  --region us-east-1
```

**Options:**
- `--name NAME` (required) - Environment name
- `--workspace WORKSPACE` (required) - Workspace name or ID
- `--cloud CLOUD` - Cloud provider: `aws`, `azure`, `gcp`
- `--region REGION` - Cloud region

## Stack Commands

### `iltero stack`

Manage infrastructure stacks.

#### `iltero stack list`

List all stacks.

```bash
iltero stack list

# Filter by workspace
iltero stack list --workspace production-infra

# Filter by environment
iltero stack list --environment production
```

#### `iltero stack create`

Create a new stack.

```bash
iltero stack create \
  --name api-gateway \
  --workspace production-infra \
  --environment production \
  --repo-url https://github.com/org/infrastructure.git \
  --branch main \
  --path terraform/api-gateway
```

**Options:**
- `--name NAME` (required) - Stack name
- `--workspace WORKSPACE` (required) - Workspace name or ID
- `--environment ENV` (required) - Environment name or ID
- `--repo-url URL` - Git repository URL
- `--branch BRANCH` - Git branch (default: main)
- `--path PATH` - Path within repository (default: .)

#### `iltero stack get`

Get stack details.

```bash
iltero stack get api-gateway

# JSON output
iltero stack get api-gateway --output json
```

#### `iltero stack validate`

Run validation on a stack.

```bash
iltero stack validate --stack-id stk_abc123

# With specific policies
iltero stack validate --stack-id stk_abc123 --policies policy-1,policy-2
```

#### `iltero stack plan`

Generate Terraform plan for a stack.

```bash
iltero stack plan --stack-id stk_abc123

# With evaluation
iltero stack plan --stack-id stk_abc123 --evaluate
```

#### `iltero stack apply`

Apply Terraform changes to a stack.

```bash
iltero stack apply --stack-id stk_abc123

# Auto-approve (use with caution)
iltero stack apply --stack-id stk_abc123 --auto-approve
```

**Options:**
- `--auto-approve` - Skip approval prompt

#### Stack Variables

##### `iltero stack variables list`

List stack variables.

```bash
iltero stack variables list --stack-id stk_abc123
```

##### `iltero stack variables set`

Set a stack variable.

```bash
iltero stack variables set \
  --stack-id stk_abc123 \
  --key database_size \
  --value db.t3.medium

# Sensitive variable
iltero stack variables set \
  --stack-id stk_abc123 \
  --key api_key \
  --value "secret123" \
  --sensitive
```

##### `iltero stack variables delete`

Delete a stack variable.

```bash
iltero stack variables delete --stack-id stk_abc123 --key database_size
```

#### Stack Drift Detection

##### `iltero stack drift detect`

Detect configuration drift.

```bash
iltero stack drift detect --stack-id stk_abc123
```

##### `iltero stack drift show`

Show drift detection results.

```bash
iltero stack drift show --drift-id dft_xyz789
```

## Scan Commands

### `iltero scan`

Run compliance scans on infrastructure code.

#### `iltero scan static`

Run static analysis scan.

```bash
# Scan local directory
iltero scan static --path ./terraform

# Scan with specific scanner
iltero scan static --path ./terraform --scanner checkov

# Scan and upload to backend
iltero scan static \
  --path ./terraform \
  --stack-id stk_abc123 \
  --upload

# Scan with output format
iltero scan static \
  --path ./terraform \
  --format sarif \
  --output scan-results.sarif
```

**Options:**
- `--path PATH` (required) - Path to scan
- `--scanner SCANNER` - Scanner to use: `checkov`, `opa`, `all` (default: all)
- `--stack-id STACK_ID` - Associate with stack
- `--upload` - Upload results to backend
- `--format FORMAT` - Output format: `json`, `sarif`, `junit`
- `--output FILE` - Write results to file

#### `iltero scan results`

View and manage scan results.

##### `iltero scan results show`

Display scan results.

```bash
iltero scan results show --scan-id scn_abc123

# JSON output
iltero scan results show --scan-id scn_abc123 --output json
```

##### `iltero scan results export`

Export scan results.

```bash
# Export as SARIF
iltero scan results export --scan-id scn_abc123 --format sarif > results.sarif

# Export as JUnit XML
iltero scan results export --scan-id scn_abc123 --format junit > results.xml
```

## Scanner Commands

### `iltero scanner`

Manage and check scanner availability.

#### `iltero scanner check`

Check if scanners are installed and available.

```bash
iltero scanner check

# Output:
# Scanner Status:
# ✓ checkov - v2.4.9 (installed)
# ✓ opa - v0.58.0 (installed)
```

**JSON output:**
```bash
iltero scanner check --output json
```

```json
{
  "checkov": {
    "installed": true,
    "version": "2.4.9",
    "path": "/usr/local/bin/checkov"
  },
  "opa": {
    "installed": true,
    "version": "0.58.0",
    "path": "/usr/local/bin/opa"
  }
}
```

## Compliance Commands

### `iltero compliance`

View and manage compliance violations.

#### `iltero compliance violations list`

List compliance violations.

```bash
# List all violations
iltero compliance violations list

# Filter by severity
iltero compliance violations list --severity critical

# Filter by status
iltero compliance violations list --status open

# Filter by workspace
iltero compliance violations list --workspace production-infra
```

**Options:**
- `--severity SEVERITY` - Filter by severity: `critical`, `high`, `medium`, `low`, `info`
- `--status STATUS` - Filter by status: `open`, `remediated`, `suppressed`
- `--workspace WORKSPACE` - Filter by workspace

#### `iltero compliance violations get`

Get violation details.

```bash
iltero compliance violations get vio_abc123
```

#### `iltero compliance violations remediate`

Mark violation as remediated.

```bash
iltero compliance violations remediate vio_abc123 \
  --note "Fixed in PR #456"
```

#### `iltero compliance dashboard`

View compliance dashboard.

```bash
iltero compliance dashboard --workspace production-infra
```

## Context Commands

### `iltero context`

Manage CLI context (default workspace, environment, etc.).

#### `iltero context show`

Display current context.

```bash
iltero context show

# Output:
# Current Context:
# Organization: my-org
# Workspace: production-infra
# Environment: production
```

#### `iltero context set`

Set context values.

```bash
# Set workspace
iltero context set workspace production-infra

# Set environment
iltero context set environment production

# Set organization
iltero context set org my-org
```

#### `iltero context clear`

Clear all context values.

```bash
iltero context clear

# Clear specific context
iltero context clear workspace
```

## Repository Commands

### `iltero repository`

Manage Git repository integrations.

#### `iltero repository list`

List connected repositories.

```bash
iltero repository list --workspace production-infra
```

#### `iltero repository connect`

Connect a Git repository.

```bash
iltero repository connect \
  --url https://github.com/org/infrastructure.git \
  --workspace production-infra
```

## Bundles Commands

### `iltero bundles`

Manage compliance bundles and policies.

#### `iltero bundles list`

List available bundles.

```bash
iltero bundles list

# Filter by category
iltero bundles list --category security
```

#### `iltero bundles marketplace`

Browse marketplace bundles.

```bash
iltero bundles marketplace
```

## Registry Commands

### `iltero registry`

Manage module and template registry.

#### `iltero registry modules list`

List registry modules.

```bash
iltero registry modules list
```

#### `iltero registry modules publish`

Publish a module to the registry.

```bash
iltero registry modules publish \
  --path ./my-module \
  --version 1.0.0
```

## Organization Commands

### `iltero org`

Manage organizations.

#### `iltero org list`

List organizations you belong to.

```bash
iltero org list
```

#### `iltero org get`

Get organization details.

```bash
iltero org get my-org
```

## User Commands

### `iltero user`

Manage users and permissions.

#### `iltero user list`

List users in organization.

```bash
iltero user list --org my-org
```

#### `iltero user invite`

Invite a user to organization.

```bash
iltero user invite \
  --email new.user@company.com \
  --org my-org \
  --role developer
```

---

## Exit Codes

The CLI uses standard exit codes:

- `0` - Success
- `1` - General error
- `2` - Authentication error
- `3` - Validation error
- `4` - Scan found violations above threshold
- `5` - Network/API error

## Output Formats

All commands support multiple output formats:

### Table (Default)

Human-readable formatted table:
```bash
iltero workspace list
```

### JSON

Machine-readable JSON:
```bash
iltero workspace list --output json
```

### YAML

YAML format:
```bash
iltero workspace list --output yaml
```

## Examples

See the [examples directory](examples/) for complete workflow examples:

- [CI/CD Integration](examples/cicd/)
- [Multi-workspace Setup](examples/multi-workspace/)
- [Custom Scanning Workflows](examples/scanning/)
