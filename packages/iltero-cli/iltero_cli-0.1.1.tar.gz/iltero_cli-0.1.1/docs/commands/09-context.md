# Context Commands

Manage CLI context (default workspace, environment, org).

## Overview

Context allows you to set default values for workspace, environment, and organization, so you don't need to specify them with every command.

## Commands

### `iltero context show`

Display current context.

```bash
iltero context show

# Output:
# Current Context:
# Organization: my-org
# Workspace: production-infra
# Environment: production
```

**JSON output:**
```bash
iltero context show --output json
```

```json
{
  "organization": "my-org",
  "workspace": "production-infra",
  "environment": "production"
}
```

### `iltero context set`

Set context values.

```bash
# Set workspace
iltero context set workspace production-infra

# Set environment
iltero context set environment production

# Set organization
iltero context set org my-org
```

**Examples:**

```bash
# Set all context values
iltero context set org acme-corp
iltero context set workspace production-infra
iltero context set environment production

# Verify context
iltero context show

# Now commands use context automatically
iltero stack list  # Lists stacks in production-infra workspace
iltero environment list  # Lists environments in production-infra
```

### `iltero context clear`

Clear context values.

```bash
# Clear all context
iltero context clear

# Clear specific context
iltero context clear workspace
iltero context clear environment
iltero context clear org
```

## Usage Examples

### Without Context

```bash
# Every command needs workspace/environment
iltero stack list --workspace production-infra
iltero environment list --workspace production-infra
iltero compliance violations list --workspace production-infra
```

### With Context

```bash
# Set once
iltero context set workspace production-infra
iltero context set environment production

# Use everywhere
iltero stack list
iltero environment list
iltero compliance violations list
```

### Temporary Override

```bash
# Set default context
iltero context set workspace production-infra

# Most commands use production-infra
iltero stack list

# But you can override when needed
iltero stack list --workspace staging-infra
```

## Best Practices

### Development Workflow

```bash
# Set context for daily work
iltero context set workspace my-team-workspace
iltero context set environment development

# Work with context
iltero stack list
iltero scan static --path ./terraform
iltero compliance violations list
```

### Multi-Environment Workflow

```bash
# Switch to production
iltero context set workspace production-infra
iltero context set environment production
iltero stack list

# Switch to staging
iltero context set workspace staging-infra
iltero context set environment staging
iltero stack list
```

### CI/CD

```bash
# In CI/CD, use explicit flags instead of context
iltero stack validate \
  --stack-id $STACK_ID \
  --workspace $WORKSPACE \
  --environment $ENVIRONMENT
```

## Context Storage

Context is stored in:
- **File:** `~/.iltero/context.yaml`
- **Per-user:** Each user has their own context
- **Not committed:** Context is local to your machine

**Example context file:**
```yaml
# ~/.iltero/context.yaml
organization: acme-corp
workspace: production-infra
environment: production
```

## Troubleshooting

### Context Not Applied

```bash
# Verify context is set
iltero context show

# If empty, set it
iltero context set workspace my-workspace
```

### Wrong Context

```bash
# Clear and reset
iltero context clear
iltero context set workspace correct-workspace
iltero context set environment production
```

## See Also

- [Workspace Commands](workspace.md) - Manage workspaces
- [Environment Commands](environment.md) - Manage environments
- [Organization Commands](org.md) - Manage organizations
- [Configuration Guide](../configuration.md) - CLI configuration

---

**Next:** [Learn about configuration](../configuration.md)
