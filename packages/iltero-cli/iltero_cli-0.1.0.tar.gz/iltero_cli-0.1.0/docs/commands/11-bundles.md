# Bundles Commands

Manage compliance bundles and policies.

## Overview

Bundles are collections of compliance policies that can be applied to your infrastructure.

## Commands

### `iltero bundles list`

List available bundles.

```bash
iltero bundles list

# Filter by category
iltero bundles list --category security
```

**Options:**
- `--category CATEGORY` - Filter by category: `security`, `compliance`, `best-practices`
- `--output FORMAT` - Output format: `table`, `json`, `yaml`

**Example output:**
```
ID            Name                      Category        Policies  Status
───────────────────────────────────────────────────────────────────────────
bun_abc123    CIS AWS Benchmark         security        247       Active
bun_def456    PCI DSS Compliance        compliance      156       Active
bun_ghi789    AWS Best Practices        best-practices  89        Active
```

### `iltero bundles get`

Get bundle details.

```bash
iltero bundles get bun_abc123

# JSON output
iltero bundles get bun_abc123 --output json
```

### `iltero bundles marketplace`

Browse marketplace bundles.

```bash
iltero bundles marketplace

# Search marketplace
iltero bundles marketplace --search "kubernetes"
```

### `iltero bundles install`

Install a bundle from the marketplace.

```bash
iltero bundles install bun_abc123 --workspace production-infra
```

### `iltero bundles uninstall`

Uninstall a bundle.

```bash
iltero bundles uninstall bun_abc123 --workspace production-infra
```

## Use Cases

### Install Security Bundle

```bash
# Browse available bundles
iltero bundles list --category security

# Get details
iltero bundles get bun_cis_aws

# Install to workspace
iltero bundles install bun_cis_aws --workspace production-infra
```

### Apply Compliance Framework

```bash
# Install PCI DSS bundle
iltero bundles install bun_pci_dss --workspace payment-processing

# Install SOC 2 bundle
iltero bundles install bun_soc2 --workspace production-infra
```

## See Also

- [Scan Commands](scan.md) - Scan against bundle policies
- [Compliance Commands](compliance.md) - View bundle violations

---

**Next:** [Scan with bundles](scan.md)
