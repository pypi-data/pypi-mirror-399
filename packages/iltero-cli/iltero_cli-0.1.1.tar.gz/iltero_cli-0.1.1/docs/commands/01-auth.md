# Authentication Commands

Manage authentication and API tokens for Iltero CLI.

## Overview

The `iltero auth` command group helps you:
- Store API tokens securely in your system keyring
- Verify authentication status
- Check connectivity to the Iltero backend
- View information about the authenticated user

## Commands

### `iltero auth set-token`

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

**Storage locations:**
- **macOS**: Keychain
- **Windows**: Credential Manager
- **Linux**: Secret Service (gnome-keyring, kwallet) or encrypted file

**Example:**
```bash
$ iltero auth set-token
Enter your Iltero API token: [hidden]
✓ Token stored successfully in system keyring

# Verify it worked
$ iltero auth status
✓ Authenticated as: john.doe@company.com
```

---

### `iltero auth show-token`

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

**Security Warning:** Be careful when using `--reveal` - avoid running this command where others can see your screen or in environments that log command output.

---

### `iltero auth status`

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

**Use cases:**
- Verify authentication before running other commands
- Troubleshoot connection issues
- Check which token type is being used
- Validate token in CI/CD pipelines

---

### `iltero auth clear-token`

Remove the stored token from the keyring.

```bash
iltero auth clear-token
# Output: ✓ Token cleared successfully
```

**Use cases:**
- Switch to a different token
- Remove credentials from a shared machine
- Troubleshoot authentication issues

**Note:** This only removes the token from the keyring. If you're using the `ILTERO_TOKEN` environment variable, you'll need to unset it separately.

---

### `iltero auth whoami`

Display information about the authenticated user.

```bash
iltero auth whoami

# Output:
# User: john.doe@company.com
# Name: John Doe
# Organization: ACME Corp
# Role: Developer
```

**JSON output:**
```bash
iltero auth whoami --output json
```

```json
{
  "email": "john.doe@company.com",
  "name": "John Doe",
  "organization": "ACME Corp",
  "role": "Developer",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

## Authentication Methods

### System Keyring (Recommended for Local Development)

```bash
# Store token in keyring
iltero auth set-token

# All subsequent commands use the stored token automatically
iltero workspace list
```

### Environment Variable (Recommended for CI/CD)

```bash
# Set environment variable
export ILTERO_TOKEN=itk_p_your_pipeline_token

# Or inline for single command
ILTERO_TOKEN=itk_p_your_token iltero workspace list
```

### Configuration File

```yaml
# ~/.iltero/config.yaml
token: itk_u_your_token_here
```

**⚠️ Warning:** Storing tokens in config files is less secure than using the keyring. Use environment variables or keyring instead.

## Authentication Precedence

The CLI checks for authentication in this order:

1. **Command-line flag** (not recommended, for testing only)
2. **Environment variable** `ILTERO_TOKEN`
3. **System keyring** (stored via `iltero auth set-token`)
4. **Config file** `~/.iltero/config.yaml`

## Token Types

Different token types have different prefixes:

| Type | Prefix | Use Case |
|------|--------|----------|
| Personal | `itk_u_` | Local development, personal use |
| Pipeline | `itk_p_` | CI/CD pipelines, automation |
| Service | `itk_s_` | Long-running services, integrations |
| Registry | `itk_r_` | Publishing to registry |

## Troubleshooting

### "Authentication failed" Error

```bash
# Check auth status
iltero auth status

# Verify token is correct
iltero auth show-token --reveal

# Try setting token again
iltero auth set-token
```

### Keyring Not Available (Linux)

If you get keyring errors on Linux:

```bash
# Install keyring backend
sudo apt install gnome-keyring  # Ubuntu/Debian

# Or use environment variable instead
export ILTERO_TOKEN=your_token
```

### CI/CD Authentication

For CI/CD pipelines, always use environment variables:

```yaml
# GitHub Actions
env:
  ILTERO_TOKEN: ${{ secrets.ILTERO_PIPELINE_TOKEN }}

# GitLab CI
variables:
  ILTERO_TOKEN: $ILTERO_PIPELINE_TOKEN
```

## See Also

- [Token Management Commands](token.md) - Create and manage tokens
- [Configuration Guide](../configuration.md) - Configure authentication methods
- [CI/CD Integration](../ci-cd/README.md) - Set up authentication in pipelines
- [Troubleshooting Guide](../troubleshooting.md) - Authentication issues

---

**Next Steps:**
- [Create tokens for different use cases](token.md)
- [Set up your first workspace](workspace.md)
- [Run your first scan](scan.md)
