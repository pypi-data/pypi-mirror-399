# Organization Commands

Manage organizations.

## Overview

Organizations are the top-level entity in Iltero that contain workspaces, users, and resources.

## Commands

### `iltero org list`

List organizations you belong to.

```bash
iltero org list

# JSON output
iltero org list --output json
```

**Example output:**
```
ID          Name          Role         Workspaces  Users
──────────────────────────────────────────────────────────
org_abc123  ACME Corp     Admin        12          45
org_def456  Startup Inc   Developer    3           8
```

### `iltero org get`

Get organization details.

```bash
iltero org get my-org

# JSON output
iltero org get my-org --output json
```

**Example output:**
```
Organization: ACME Corp
ID: org_abc123
Created: 2024-01-15

Statistics:
  Workspaces: 12
  Users: 45
  Stacks: 127
  Active Scans: 15

Settings:
  Default Workspace: production-infra
  Compliance Frameworks: CIS AWS, SOC 2, PCI DSS
  SSO Enabled: Yes
```

### `iltero org create`

Create a new organization.

```bash
iltero org create \
  --name "My Organization" \
  --description "Company infrastructure"
```

### `iltero org update`

Update organization settings.

```bash
iltero org update my-org \
  --description "Updated description"
```

### `iltero org delete`

Delete an organization.

```bash
iltero org delete my-org --force
```

**⚠️ Warning:** This will delete all workspaces, stacks, and data. Cannot be undone.

## Organization Settings

### `iltero org settings get`

Get organization settings.

```bash
iltero org settings get my-org
```

### `iltero org settings update`

Update organization settings.

```bash
iltero org settings update my-org \
  --default-workspace production-infra \
  --sso-enabled true
```

## See Also

- [Workspace Commands](workspace.md) - Create workspaces in organization
- [User Commands](user.md) - Manage organization users
- [Context Commands](context.md) - Set default organization

---

**Next:** [Create workspaces](workspace.md)
