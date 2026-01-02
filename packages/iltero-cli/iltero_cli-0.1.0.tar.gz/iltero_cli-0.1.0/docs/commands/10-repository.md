# Repository Commands

Manage Git repository integrations.

## Overview

Connect Git repositories to Iltero for automatic scanning and stack management.

## Commands

### `iltero repository list`

List connected repositories.

```bash
iltero repository list --workspace production-infra

# JSON output
iltero repository list --workspace production-infra --output json
```

### `iltero repository connect`

Connect a Git repository.

```bash
iltero repository connect \
  --url https://github.com/org/infrastructure.git \
  --workspace production-infra
```

**Options:**
- `--url URL` (required) - Git repository URL
- `--workspace WORKSPACE` (required) - Workspace name or ID
- `--branch BRANCH` - Default branch (default: main)
- `--credentials CREDS` - Git credentials (if private repo)

### `iltero repository disconnect`

Disconnect a repository.

```bash
iltero repository disconnect repo_abc123
```

## See Also

- [Stack Commands](stack.md) - Create stacks from repositories
- [Scan Commands](scan.md) - Scan repository code

---

**Next:** [Create stacks from repositories](stack.md)
