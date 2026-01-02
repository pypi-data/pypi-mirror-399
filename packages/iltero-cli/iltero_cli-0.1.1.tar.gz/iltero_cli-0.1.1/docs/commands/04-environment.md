# Environment Commands

Manage environments within workspaces.

## Overview

Environments represent deployment targets within a workspace (e.g., production, staging, development).

## Commands

### `iltero environment list`

List environments in a workspace.

```bash
iltero environment list --workspace production-infra

# Using context
iltero context set workspace production-infra
iltero environment list
```

### `iltero environment create`

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

**Examples:**

```bash
# Create production environment
iltero environment create \
  --name production \
  --workspace my-workspace \
  --cloud aws \
  --region us-east-1

# Create staging environment
iltero environment create \
  --name staging \
  --workspace my-workspace \
  --cloud aws \
  --region us-west-2
```

### `iltero environment get`

Get environment details.

```bash
iltero environment get production --workspace my-workspace
```

### `iltero environment update`

Update environment settings.

```bash
iltero environment update production \
  --workspace my-workspace \
  --region us-east-2
```

### `iltero environment delete`

Delete an environment.

```bash
iltero environment delete production --workspace my-workspace --force
```

## See Also

- [Workspace Commands](workspace.md) - Manage workspaces
- [Stack Commands](stack.md) - Create stacks in environments
- [Context Commands](context.md) - Set default environment

---

**Next:** [Create infrastructure stacks](stack.md)
