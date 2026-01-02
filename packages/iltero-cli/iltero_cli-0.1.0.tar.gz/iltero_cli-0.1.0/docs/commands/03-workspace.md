# Workspace Commands

Manage workspaces - isolated environments for organizing infrastructure stacks.

## Overview

Workspaces provide isolated environments to organize your infrastructure stacks, compliance policies, and team access. Think of workspaces as top-level containers for related infrastructure.

## Commands

### `iltero workspace list`

List all workspaces you have access to.

```bash
iltero workspace list

# With filters
iltero workspace list --org my-org --status active

# JSON output
iltero workspace list --output json
```

**Options:**
- `--org ORG` - Filter by organization
- `--status STATUS` - Filter by status: `active`, `archived`
- `--output FORMAT` - Output format: `table`, `json`, `yaml`

**Example output:**
```
ID           Name              Organization  Environments  Stacks  Status
────────────────────────────────────────────────────────────────────────────
wsp_abc123   production-infra  ACME Corp     3             12      Active
wsp_def456   staging-infra     ACME Corp     2             8       Active
wsp_ghi789   dev-sandbox       ACME Corp     1             3       Active
```

---

### `iltero workspace create`

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
- `--org ORG` - Organization (uses default from context if not specified)
- `--tags TAGS` - Comma-separated tags (e.g., `env:prod,team:platform`)

**Example:**
```bash
iltero workspace create \
  --name production-aws \
  --description "Production AWS infrastructure" \
  --org acme-corp \
  --tags "cloud:aws,env:production,team:platform"
```

**Output:**
```
✓ Workspace created successfully

Workspace ID: wsp_xyz789
Name: production-aws
Organization: acme-corp
Status: Active

Next steps:
  1. Create an environment: iltero environment create --workspace production-aws
  2. Create a stack: iltero stack create --workspace production-aws
  3. Set as default: iltero context set workspace production-aws
```

---

### `iltero workspace get`

Get detailed information about a workspace.

```bash
iltero workspace get production-infra

# By ID
iltero workspace get wsp_abc123

# JSON output
iltero workspace get production-infra --output json
```

**Example output:**
```
Workspace: production-infra
ID: wsp_abc123
Organization: ACME Corp
Description: Production infrastructure workspace
Status: Active
Created: 2024-01-15 10:30:00
Tags: cloud:aws, env:production

Environments:
  - production (env_123)
  - staging (env_456)
  - qa (env_789)

Statistics:
  Stacks: 12
  Active Scans: 3
  Violations: 5 (2 critical, 3 high)
```

---

### `iltero workspace update`

Update workspace settings.

```bash
iltero workspace update production-infra \
  --description "Updated description" \
  --tags "environment:prod,team:platform,cloud:aws"
```

**Options:**
- `--description DESC` - New description
- `--tags TAGS` - Comma-separated tags (replaces existing tags)
- `--name NAME` - Rename workspace

**Example:**
```bash
# Update description
iltero workspace update production-infra \
  --description "Production AWS infrastructure for web services"

# Update tags
iltero workspace update production-infra \
  --tags "cloud:aws,env:prod,team:platform,criticality:high"

# Rename workspace
iltero workspace update old-name --name new-name
```

---

### `iltero workspace delete`

Delete a workspace and all its contents.

```bash
iltero workspace delete production-infra

# Force delete without confirmation
iltero workspace delete production-infra --force
```

**Options:**
- `--force` - Skip confirmation prompt

**⚠️ Warning:** Deleting a workspace will:
- Delete all environments within the workspace
- Delete all stacks within the workspace
- Delete all scan history
- Remove all compliance data
- This action **cannot be undone**

**Example:**
```bash
# With confirmation
$ iltero workspace delete test-workspace
⚠️  Are you sure you want to delete workspace 'test-workspace'? 
    This will delete 2 environments, 5 stacks, and all scan history.
    Type 'test-workspace' to confirm: test-workspace
✓ Workspace deleted successfully

# Without confirmation (use with extreme caution)
iltero workspace delete temp-workspace --force
```

---

## Workspace Organization

### Use Cases

**Separate by Environment Tier:**
```bash
iltero workspace create --name production
iltero workspace create --name staging
iltero workspace create --name development
```

**Separate by Cloud Provider:**
```bash
iltero workspace create --name aws-infrastructure
iltero workspace create --name azure-infrastructure
iltero workspace create --name gcp-infrastructure
```

**Separate by Team or Product:**
```bash
iltero workspace create --name platform-team
iltero workspace create --name product-api
iltero workspace create --name data-pipeline
```

**Separate by Customer (Multi-tenant):**
```bash
iltero workspace create --name customer-acme
iltero workspace create --name customer-globex
```

### Tagging Strategy

Use tags to add metadata to workspaces:

```bash
# Cloud provider
--tags "cloud:aws"
--tags "cloud:azure"
--tags "cloud:gcp"
--tags "cloud:multi"

# Environment
--tags "env:production"
--tags "env:staging"
--tags "env:development"

# Team ownership
--tags "team:platform"
--tags "team:security"
--tags "team:data"

# Criticality
--tags "criticality:high"
--tags "criticality:medium"
--tags "criticality:low"

# Compliance requirements
--tags "compliance:soc2"
--tags "compliance:hipaa"
--tags "compliance:pci"

# Combine multiple tags
iltero workspace create --name prod-api \
  --tags "cloud:aws,env:production,team:api,criticality:high,compliance:soc2"
```

---

## Workflow Examples

### Initial Setup

```bash
# 1. Create workspace
iltero workspace create \
  --name production-infra \
  --description "Production infrastructure" \
  --tags "env:prod,cloud:aws"

# 2. Set as default context
iltero context set workspace production-infra

# 3. Create environments
iltero environment create \
  --name production \
  --workspace production-infra \
  --cloud aws \
  --region us-east-1

# 4. Create stacks
iltero stack create \
  --name api-gateway \
  --workspace production-infra \
  --environment production \
  --repo-url https://github.com/org/infra.git
```

### Multi-Environment Setup

```bash
# Create workspace for each environment
for env in production staging development; do
  iltero workspace create \
    --name "${env}-infra" \
    --description "${env} environment infrastructure" \
    --tags "env:${env}"
done

# List all workspaces
iltero workspace list
```

### Workspace Migration

```bash
# 1. Create new workspace
iltero workspace create \
  --name new-production \
  --description "New production workspace"

# 2. List stacks in old workspace
iltero stack list --workspace old-production --output json > stacks.json

# 3. Recreate stacks in new workspace
# (Use scripts to parse stacks.json and create in new workspace)

# 4. Verify migration
iltero workspace get new-production

# 5. Archive old workspace
iltero workspace delete old-production
```

---

## Working with Context

Set a default workspace to avoid specifying `--workspace` on every command:

```bash
# Set default workspace
iltero context set workspace production-infra

# Now these commands use production-infra automatically
iltero environment list
iltero stack list
iltero compliance violations list

# View current context
iltero context show

# Override context temporarily
iltero stack list --workspace staging-infra

# Clear context
iltero context clear workspace
```

---

## Best Practices

### Naming Conventions

**✅ Good names:**
- `production-aws` - Clear and specific
- `staging-api` - Indicates environment and purpose
- `customer-acme` - Identifies customer in multi-tenant setup

**❌ Avoid:**
- `workspace1` - Not descriptive
- `test` - Too generic
- `johns-workspace` - User-specific (use for personal development only)

### Organization Strategy

1. **Start simple** - Create workspaces by environment (prod, staging, dev)
2. **Scale with structure** - Add more workspaces as needed (by team, product, cloud, etc.)
3. **Use consistent tagging** - Apply the same tag scheme across all workspaces
4. **Document purpose** - Use descriptions to explain workspace purpose
5. **Regular cleanup** - Delete unused workspaces to reduce clutter

### Access Control

Workspaces provide permission boundaries:

```bash
# Production workspace - restricted access
iltero workspace create --name production
# Grant access to: platform team, security team
# Permissions: Read/write for platform team, read-only for others

# Development workspace - open access
iltero workspace create --name development
# Grant access to: all engineers
# Permissions: Full read/write access
```

---

## Troubleshooting

### Workspace Not Found

```bash
# List all accessible workspaces
iltero workspace list

# Check if workspace was deleted
iltero workspace list --status archived

# Verify workspace name (case-sensitive)
iltero workspace get PRODUCTION-INFRA  # Wrong
iltero workspace get production-infra   # Correct
```

### Permission Denied

```bash
# Verify you have access to the workspace
iltero workspace list

# Check your role
iltero auth whoami

# Contact workspace administrator for access
```

### Cannot Delete Workspace

```bash
# Check workspace contents
iltero workspace get my-workspace

# Delete stacks first
iltero stack list --workspace my-workspace
iltero stack delete stack-1 --force
iltero stack delete stack-2 --force

# Then delete workspace
iltero workspace delete my-workspace --force
```

---

## See Also

- [Environment Commands](environment.md) - Manage environments within workspaces
- [Stack Commands](stack.md) - Manage stacks within workspaces
- [Context Commands](context.md) - Set default workspace
- [Organization Commands](org.md) - Manage organizations

---

**Next Steps:**
- [Create environments in your workspace](environment.md)
- [Create infrastructure stacks](stack.md)
- [Set up default context](context.md)
