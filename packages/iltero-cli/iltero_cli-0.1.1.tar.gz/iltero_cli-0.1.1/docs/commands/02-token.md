# Token Commands

Create and manage API tokens for Iltero CLI.

## Overview

The `iltero token` command group allows you to:
- Create new API tokens (personal, pipeline, service, registry)
- List existing tokens
- Revoke tokens when no longer needed

## Commands

### `iltero token list`

List all tokens for the authenticated user.

```bash
iltero token list

# Table output:
# ID          Name              Type      Created              Last Used            Status
# ────────────────────────────────────────────────────────────────────────────────────────
# tok_abc123  My Personal       Personal  2024-01-15 10:30:00  2024-12-04 14:20:00  Active
# tok_def456  CI/CD Pipeline    Pipeline  2024-02-01 08:15:00  2024-12-04 12:00:00  Active
# tok_ghi789  GitHub Actions    Pipeline  2024-03-10 09:00:00  Never                Active
```

**Options:**
- `--type TYPE` - Filter by token type: `personal`, `pipeline`, `service`, `registry`
- `--status STATUS` - Filter by status: `active`, `revoked`
- `--output FORMAT` - Output format: `table`, `json`, `yaml`

**Examples:**

```bash
# List only pipeline tokens
iltero token list --type pipeline

# List revoked tokens
iltero token list --status revoked

# JSON output
iltero token list --output json
```

**JSON output:**
```json
{
  "tokens": [
    {
      "id": "tok_abc123",
      "name": "My Personal",
      "type": "personal",
      "prefix": "itk_u",
      "created_at": "2024-01-15T10:30:00Z",
      "last_used_at": "2024-12-04T14:20:00Z",
      "status": "active",
      "expires_at": null
    }
  ]
}
```

---

### `iltero token create`

Create a new API token.

```bash
# Create personal token
iltero token create --name "My Development Token" --type personal

# Create pipeline token
iltero token create --name "GitHub Actions" --type pipeline --expires-in 90

# Create service token
iltero token create --name "Monitoring Service" --type service

# Create registry token
iltero token create --name "Module Publisher" --type registry
```

**Options:**
- `--name NAME` (required) - Token name/description
- `--type TYPE` (required) - Token type: `personal`, `pipeline`, `service`, `registry`
- `--expires-in DAYS` - Token expiration in days (optional, default: no expiration)
- `--scopes SCOPES` - Comma-separated scopes (optional)

**Output:**
```
✓ Token created successfully

Token ID: tok_xyz789
Token: itk_p_abcdefghijklmnopqrstuvwxyz1234567890

⚠️  Save this token now - you won't see it again!
```

**⚠️ Important:** Save the token immediately! For security reasons, the full token value is only displayed once at creation time.

**Examples:**

```bash
# Create personal token for local development
iltero token create \
  --name "MacBook Development" \
  --type personal

# Create pipeline token with expiration
iltero token create \
  --name "Staging Pipeline" \
  --type pipeline \
  --expires-in 365

# Create service token with limited scopes
iltero token create \
  --name "Monitoring Service" \
  --type service \
  --scopes "read:stacks,read:compliance"
```

---

### `iltero token revoke`

Revoke an API token, making it invalid for authentication.

```bash
iltero token revoke tok_abc123

# With confirmation prompt:
# ⚠️  Are you sure you want to revoke token 'GitHub Actions' (tok_abc123)? [y/N]: y
# ✓ Token revoked successfully
```

**Options:**
- `--confirm` - Skip confirmation prompt (useful for scripts)

**Examples:**

```bash
# Revoke with confirmation
iltero token revoke tok_abc123

# Revoke without confirmation (use with caution)
iltero token revoke tok_abc123 --confirm
```

**⚠️ Warning:** Revoking a token is permanent and cannot be undone. Any systems using that token will immediately lose access.

---

## Token Types

### Personal Token (`itk_u_*`)

**Use for:**
- Local development on your machine
- Interactive CLI usage
- Testing and experimentation

**Characteristics:**
- Tied to your user account
- Inherits your permissions
- Can be stored in system keyring

**Example:**
```bash
iltero token create --name "Development Laptop" --type personal
```

---

### Pipeline Token (`itk_p_*`)

**Use for:**
- CI/CD pipelines (GitHub Actions, GitLab CI, Jenkins, etc.)
- Automated workflows
- Temporary automation tasks

**Characteristics:**
- Designed for automation
- Can set expiration dates
- Best practice: one token per pipeline

**Example:**
```bash
iltero token create \
  --name "Production Deploy Pipeline" \
  --type pipeline \
  --expires-in 365
```

---

### Service Token (`itk_s_*`)

**Use for:**
- Long-running services
- Monitoring systems
- Integration platforms
- Scheduled tasks

**Characteristics:**
- Long-lived (no expiration by default)
- Can have restricted scopes
- Suitable for production services

**Example:**
```bash
iltero token create \
  --name "Compliance Monitor" \
  --type service \
  --scopes "read:compliance,read:stacks"
```

---

### Registry Token (`itk_r_*`)

**Use for:**
- Publishing modules to the registry
- Downloading private modules
- Registry operations

**Characteristics:**
- Registry-specific permissions
- Can publish and manage modules

**Example:**
```bash
iltero token create \
  --name "Module Publisher" \
  --type registry
```

---

## Token Scopes

Limit token permissions with scopes:

| Scope | Description |
|-------|-------------|
| `read:stacks` | Read stack information |
| `write:stacks` | Create/update stacks |
| `read:compliance` | View compliance data |
| `write:compliance` | Manage violations |
| `read:scans` | View scan results |
| `write:scans` | Run scans |
| `admin:workspace` | Workspace administration |
| `admin:org` | Organization administration |

**Example with scopes:**
```bash
iltero token create \
  --name "Read-Only Monitor" \
  --type service \
  --scopes "read:stacks,read:compliance,read:scans"
```

---

## Best Practices

### Token Management

1. **Use descriptive names** - Include purpose and location
   ```bash
   iltero token create --name "GitHub Actions - Production" --type pipeline
   ```

2. **Set expiration dates** - Especially for pipeline tokens
   ```bash
   iltero token create --name "Temporary Test" --type pipeline --expires-in 30
   ```

3. **Rotate regularly** - Create new tokens, revoke old ones
   ```bash
   # Create new token
   iltero token create --name "New Pipeline Token" --type pipeline
   
   # Update CI/CD secrets
   # ...
   
   # Revoke old token
   iltero token revoke tok_old123
   ```

4. **Use minimal scopes** - Grant only necessary permissions
   ```bash
   iltero token create \
     --name "Scan Service" \
     --type service \
     --scopes "read:stacks,write:scans"
   ```

### Token Storage

**✅ Do:**
- Store tokens in CI/CD platform secrets (GitHub Secrets, GitLab Variables, etc.)
- Use system keyring for local development
- Use environment variables for temporary access
- Encrypt tokens if storing in files

**❌ Don't:**
- Commit tokens to version control
- Share tokens via email or chat
- Hardcode tokens in scripts
- Store tokens in plain text files

### Token Security

```bash
# Good: Environment variable in CI/CD
env:
  ILTERO_TOKEN: ${{ secrets.ILTERO_PIPELINE_TOKEN }}

# Good: System keyring for local use
iltero auth set-token

# Bad: Hardcoded in script
ILTERO_TOKEN="itk_p_abc123..." iltero scan static  # ❌ Never do this!

# Bad: In version control
echo "token: itk_p_abc123..." > config.yaml  # ❌ Never do this!
```

---

## Workflow Examples

### Setting Up CI/CD

```bash
# 1. Create pipeline token
iltero token create \
  --name "GitHub Actions - Main Branch" \
  --type pipeline \
  --expires-in 365

# 2. Copy the token (shown only once)
# Token: itk_p_abc123xyz...

# 3. Add to GitHub Secrets
# Repository Settings → Secrets → New secret
# Name: ILTERO_PIPELINE_TOKEN
# Value: itk_p_abc123xyz...

# 4. Use in workflow
# .github/workflows/compliance.yml
env:
  ILTERO_TOKEN: ${{ secrets.ILTERO_PIPELINE_TOKEN }}
```

### Rotating Tokens

```bash
# 1. List current tokens
iltero token list

# 2. Create new token
NEW_TOKEN=$(iltero token create \
  --name "Rotated Pipeline Token" \
  --type pipeline \
  --output json | jq -r '.token')

# 3. Update systems with new token
# ... update CI/CD, services, etc. ...

# 4. Revoke old token
iltero token revoke tok_old123 --confirm

# 5. Verify old token no longer works
ILTERO_TOKEN=tok_old123 iltero auth status  # Should fail
```

### Audit Token Usage

```bash
# List all tokens with last used date
iltero token list --output json | jq '.tokens[] | {name, last_used_at, status}'

# Find unused tokens (never used)
iltero token list --output json | jq '.tokens[] | select(.last_used_at == null)'

# Find tokens not used in 90 days
# (requires date comparison logic in your script)
```

---

## Troubleshooting

### Token Not Working

```bash
# 1. Verify token exists and is active
iltero token list | grep tok_abc123

# 2. Check authentication with the token
ILTERO_TOKEN=your_token iltero auth status

# 3. Verify token hasn't expired
iltero token list --output json | jq '.tokens[] | select(.id == "tok_abc123")'
```

### Lost Token

If you lose a token value:

1. **Cannot recover** - Token values are not retrievable after creation
2. **Create new token** - Generate a replacement token
3. **Revoke old token** - Revoke the lost token for security

```bash
# Create replacement
iltero token create --name "Replacement Token" --type pipeline

# Revoke lost token (if you know the ID)
iltero token revoke tok_lost123
```

### Too Many Tokens

```bash
# List all tokens
iltero token list

# Revoke unused tokens
iltero token revoke tok_unused1 --confirm
iltero token revoke tok_unused2 --confirm

# Consider token rotation policy
# Create new tokens, update systems, revoke old ones
```

---

## See Also

- [Authentication Commands](auth.md) - Store and manage tokens
- [CI/CD Integration](../ci-cd/README.md) - Use tokens in pipelines
- [Configuration Guide](../configuration.md) - Token configuration options
- [Security Best Practices](../troubleshooting.md#security) - Token security

---

**Next Steps:**
- [Set up authentication](auth.md)
- [Create your first workspace](workspace.md)
- [Configure CI/CD pipeline](../ci-cd/github-actions.md)
