# Stack Commands

Manage infrastructure stacks.

## Overview

Stacks represent infrastructure deployments managed by Terraform or other IaC tools.

## Commands

### `iltero stack list`

List all stacks.

```bash
iltero stack list

# Filter by workspace
iltero stack list --workspace production-infra

# Filter by environment
iltero stack list --environment production
```

### `iltero stack create`

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

### `iltero stack get`

Get stack details.

```bash
iltero stack get api-gateway

# JSON output
iltero stack get api-gateway --output json
```

### `iltero stack validate`

Run validation on a stack.

```bash
iltero stack validate --stack-id stk_abc123

# With specific policies
iltero stack validate --stack-id stk_abc123 --policies policy-1,policy-2
```

### `iltero stack plan`

Generate Terraform plan for a stack.

```bash
iltero stack plan --stack-id stk_abc123

# With evaluation
iltero stack plan --stack-id stk_abc123 --evaluate
```

### `iltero stack apply`

Apply Terraform changes to a stack.

```bash
iltero stack apply --stack-id stk_abc123

# Auto-approve (use with caution)
iltero stack apply --stack-id stk_abc123 --auto-approve
```

**⚠️ Warning:** `--auto-approve` skips confirmation. Use only in automation with proper safeguards.

## Stack Variables

### `iltero stack variables list`

List stack variables.

```bash
iltero stack variables list --stack-id stk_abc123
```

### `iltero stack variables set`

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

### `iltero stack variables delete`

Delete a stack variable.

```bash
iltero stack variables delete --stack-id stk_abc123 --key database_size
```

## Stack Drift Detection

### `iltero stack drift detect`

Detect configuration drift.

```bash
iltero stack drift detect --stack-id stk_abc123
```

### `iltero stack drift show`

Show drift detection results.

```bash
iltero stack drift show --drift-id dft_xyz789
```

## See Also

- [Workspace Commands](workspace.md) - Create workspaces for stacks
- [Environment Commands](environment.md) - Create environments for stacks
- [Scan Commands](scan.md) - Scan stack infrastructure code

---

**Next:** [Run compliance scans](scan.md)
