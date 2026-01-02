# User Commands

Manage users and permissions.

## Overview

Manage user access, invitations, and roles within your organization.

## Commands

### `iltero user list`

List users in organization.

```bash
iltero user list --org my-org

# Filter by role
iltero user list --org my-org --role admin
```

**Options:**
- `--org ORG` (required) - Organization name or ID
- `--role ROLE` - Filter by role: `admin`, `developer`, `viewer`
- `--status STATUS` - Filter by status: `active`, `pending`, `inactive`

**Example output:**
```
ID          Email                    Name          Role       Status
─────────────────────────────────────────────────────────────────────────
usr_abc123  john@company.com        John Doe      Admin      Active
usr_def456  jane@company.com        Jane Smith    Developer  Active
usr_ghi789  bob@company.com         Bob Johnson   Viewer     Active
usr_jkl012  alice@company.com       Alice Brown   Developer  Pending
```

### `iltero user get`

Get user details.

```bash
iltero user get john@company.com --org my-org

# By user ID
iltero user get usr_abc123
```

### `iltero user invite`

Invite a user to organization.

```bash
iltero user invite \
  --email new.user@company.com \
  --org my-org \
  --role developer
```

**Options:**
- `--email EMAIL` (required) - User email address
- `--org ORG` (required) - Organization name or ID
- `--role ROLE` (required) - User role: `admin`, `developer`, `viewer`
- `--workspaces WORKSPACES` - Comma-separated list of workspace access

**Examples:**

```bash
# Invite admin
iltero user invite \
  --email admin@company.com \
  --org my-org \
  --role admin

# Invite developer with workspace access
iltero user invite \
  --email developer@company.com \
  --org my-org \
  --role developer \
  --workspaces production-infra,staging-infra

# Invite viewer (read-only)
iltero user invite \
  --email viewer@company.com \
  --org my-org \
  --role viewer
```

### `iltero user update`

Update user role or permissions.

```bash
iltero user update usr_abc123 \
  --role admin

# Update workspace access
iltero user update usr_abc123 \
  --workspaces production-infra,staging-infra,development
```

### `iltero user remove`

Remove a user from organization.

```bash
iltero user remove usr_abc123 --org my-org

# Force remove without confirmation
iltero user remove usr_abc123 --org my-org --force
```

## User Roles

### Admin
- Full access to organization
- Manage users and permissions
- Create/delete workspaces
- Manage organization settings

### Developer
- Create and manage stacks
- Run scans and view results
- Manage compliance violations
- Access assigned workspaces

### Viewer
- Read-only access
- View stacks and scan results
- View compliance violations
- Cannot make changes

## Workflow Examples

### Onboard New Team Member

```bash
# 1. Invite user
iltero user invite \
  --email newdev@company.com \
  --org acme-corp \
  --role developer \
  --workspaces production-infra

# 2. User receives invitation email
# 3. User accepts and creates account
# 4. Verify user is active
iltero user list --org acme-corp | grep newdev@company.com
```

### Promote User to Admin

```bash
# Current role: developer
iltero user get developer@company.com --org acme-corp

# Promote to admin
iltero user update usr_abc123 --role admin

# Verify
iltero user get usr_abc123
```

### Audit User Access

```bash
# List all admins
iltero user list --org my-org --role admin

# List all pending invitations
iltero user list --org my-org --status pending

# Export user list
iltero user list --org my-org --output json > users.json
```

## Best Practices

### Principle of Least Privilege
- Start with viewer role
- Promote to developer as needed
- Limit admin access to essential personnel

### Regular Access Reviews
```bash
# Monthly access review
iltero user list --org my-org --output json > access-review-$(date +%Y-%m).json

# Review and remove inactive users
iltero user list --org my-org --status inactive
```

### Workspace-Based Access
```bash
# Production: restricted access
iltero user invite \
  --email ops@company.com \
  --org my-org \
  --role developer \
  --workspaces production-infra

# Development: broader access
iltero user invite \
  --email dev@company.com \
  --org my-org \
  --role developer \
  --workspaces development,staging-infra
```

## See Also

- [Organization Commands](org.md) - Manage organizations
- [Workspace Commands](workspace.md) - Manage workspaces
- [Token Commands](token.md) - Create access tokens

---

**Next:** [Manage organizations](org.md)
