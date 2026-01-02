# Scanner Commands

Manage and check scanner availability.

## Overview

The `iltero scanner` command helps you verify that compliance scanners are properly installed and accessible.

## Commands

### `iltero scanner check`

Check if scanners are installed and available.

```bash
iltero scanner check

# Output:
# Scanner Status:
# ✓ checkov - v2.4.9 (installed)
# ✓ opa - v0.58.0 (installed)
# ✗ custodian - Not installed
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
  },
  "custodian": {
    "installed": false
  }
}
```

## Supported Scanners

### Checkov
```bash
# Install
pip install checkov

# Verify
checkov --version
```

### OPA (Open Policy Agent)
```bash
# Install (macOS)
brew install opa

# Install (Linux)
curl -L https://openpolicyagent.org/downloads/latest/opa_linux_amd64 -o opa
chmod +x opa
sudo mv opa /usr/local/bin/

# Verify
opa version
```

### Cloud Custodian
```bash
# Install
pip install c7n c7n-org

# Verify
custodian version
```

## See Also

- [Scan Commands](scan.md) - Run compliance scans
- [Installation Guide](../installation.md) - Install scanners

---

**Next:** [Run your first scan](scan.md)
