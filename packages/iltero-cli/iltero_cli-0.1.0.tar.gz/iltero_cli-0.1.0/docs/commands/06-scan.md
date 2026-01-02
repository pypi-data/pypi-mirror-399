# Scan Commands

Run compliance scans on infrastructure code and view scan results.

## Overview

The `iltero scan` command group allows you to:
- Run static analysis on local infrastructure code
- Upload scan results to the Iltero backend
- Export results in various formats (JSON, SARIF, JUnit)
- View and manage scan results

## Commands

### `iltero scan static`

Run static analysis scan on local infrastructure code.

```bash
# Scan local directory
iltero scan static --path ./terraform

# Scan with specific scanner
iltero scan static --path ./terraform --scanner checkov

# Scan and upload to backend
iltero scan static \
  --path ./terraform \
  --stack-id stk_abc123 \
  --upload

# Scan with output format
iltero scan static \
  --path ./terraform \
  --format sarif \
  --output scan-results.sarif
```

**Options:**
- `--path PATH` (required) - Path to scan
- `--scanner SCANNER` - Scanner to use: `checkov`, `opa`, `custodian`, `all` (default: all)
- `--stack-id STACK_ID` - Associate scan with a stack
- `--upload` - Upload results to Iltero backend
- `--format FORMAT` - Output format: `json`, `sarif`, `junit`
- `--output FILE` - Write results to file
- `--fail-on SEVERITY` - Exit with error if violations found: `critical`, `high`, `medium`, `low`

**Examples:**

```bash
# Simple local scan
iltero scan static --path ./infrastructure

# Scan with Checkov only
iltero scan static --path ./terraform --scanner checkov

# Scan and upload (requires stack-id)
iltero scan static \
  --path ./terraform \
  --stack-id stk_abc123 \
  --upload

# Scan and export as SARIF for GitHub Code Scanning
iltero scan static \
  --path . \
  --format sarif \
  --output results.sarif

# Scan and fail CI if critical violations found
iltero scan static \
  --path ./terraform \
  --fail-on critical \
  --format json

# Scan with multiple scanners
iltero scan static \
  --path ./infrastructure \
  --scanner all
```

**Exit codes:**
- `0` - Scan completed, no violations (or below threshold)
- `4` - Violations found above `--fail-on` threshold
- Other codes indicate errors

---

### `iltero scan results show`

Display scan results.

```bash
iltero scan results show --scan-id scn_abc123

# JSON output
iltero scan results show --scan-id scn_abc123 --output json

# YAML output
iltero scan results show --scan-id scn_abc123 --output yaml
```

**Example output:**
```
Scan ID: scn_abc123
Stack: api-gateway (stk_xyz789)
Status: Completed
Started: 2024-12-04 10:30:00
Duration: 45 seconds

Summary:
  Total Files: 127
  Total Checks: 1,245
  Violations: 12

By Severity:
  Critical: 2
  High: 4
  Medium: 5
  Low: 1
  Info: 0

Top Violations:
  1. [CRITICAL] S3 bucket not encrypted (CKV_AWS_19)
     File: modules/storage/s3.tf:15
  
  2. [CRITICAL] RDS instance not encrypted (CKV_AWS_16)
     File: modules/database/rds.tf:42
  
  3. [HIGH] Security group allows 0.0.0.0/0 ingress (CKV_AWS_24)
     File: modules/network/security_groups.tf:8
```

---

### `iltero scan results export`

Export scan results to a file.

```bash
# Export as SARIF (for GitHub Code Scanning)
iltero scan results export --scan-id scn_abc123 --format sarif > results.sarif

# Export as JUnit XML (for CI/CD test reports)
iltero scan results export --scan-id scn_abc123 --format junit > results.xml

# Export as JSON
iltero scan results export --scan-id scn_abc123 --format json > results.json
```

**Options:**
- `--scan-id SCAN_ID` (required) - Scan ID to export
- `--format FORMAT` (required) - Export format: `sarif`, `junit`, `json`

**Use cases:**
- **SARIF** - Upload to GitHub Code Scanning, Azure DevOps, etc.
- **JUnit XML** - Display as test results in CI/CD platforms
- **JSON** - Custom processing and analysis

---

## Supported Scanners

### Checkov

Infrastructure as Code scanner supporting:
- Terraform
- CloudFormation
- Kubernetes
- Helm
- Dockerfile
- Azure Resource Manager
- And more...

**Check installation:**
```bash
iltero scanner check

# Install if needed
pip install checkov
```

### OPA (Open Policy Agent)

Policy-based compliance scanner.

**Check installation:**
```bash
iltero scanner check

# Install if needed (macOS)
brew install opa
```

### Cloud Custodian

Cloud resource compliance scanner for AWS, Azure, and GCP.

**Check installation:**
```bash
iltero scanner check

# Install if needed
pip install c7n c7n-org
```

---

## Workflow Examples

### Local Development Workflow

```bash
# 1. Check scanners are installed
iltero scanner check

# 2. Run scan on current directory
iltero scan static --path .

# 3. Review violations
# Fix any critical/high severity issues

# 4. Re-scan to verify fixes
iltero scan static --path .
```

### CI/CD Pipeline Workflow

```bash
# 1. Install CLI and scanners
pip install iltero-cli checkov

# 2. Authenticate
export ILTERO_TOKEN=$PIPELINE_TOKEN

# 3. Run scan and upload
iltero scan static \
  --path ./terraform \
  --stack-id $STACK_ID \
  --upload \
  --format json \
  --output scan-results.json

# 4. Fail if critical violations found
iltero scan static \
  --path ./terraform \
  --fail-on critical
```

### GitHub Code Scanning Integration

```bash
# 1. Run scan and export as SARIF
iltero scan static \
  --path . \
  --format sarif \
  --output results.sarif

# 2. Upload to GitHub Code Scanning (via workflow)
# - uses: github/codeql-action/upload-sarif@v2
#   with:
#     sarif_file: results.sarif
```

### Multi-Scanner Workflow

```bash
# Run all scanners
iltero scan static --path ./infrastructure --scanner all

# Run specific scanner
iltero scan static --path ./terraform --scanner checkov
iltero scan static --path ./policies --scanner opa
iltero scan static --path ./aws --scanner custodian
```

---

## Output Formats

### Table (Default)

Human-readable table format:
```bash
iltero scan static --path ./terraform
```

### JSON

Machine-readable JSON:
```bash
iltero scan static --path ./terraform --format json
```

```json
{
  "scan_id": "scn_abc123",
  "status": "completed",
  "summary": {
    "total_files": 127,
    "total_checks": 1245,
    "violations": {
      "critical": 2,
      "high": 4,
      "medium": 5,
      "low": 1
    }
  },
  "violations": [
    {
      "id": "vio_123",
      "severity": "CRITICAL",
      "rule_id": "CKV_AWS_19",
      "rule_name": "S3 bucket not encrypted",
      "file": "modules/storage/s3.tf",
      "line": 15
    }
  ]
}
```

### SARIF

Static Analysis Results Interchange Format for tool integration:
```bash
iltero scan static --path . --format sarif --output results.sarif
```

Compatible with:
- GitHub Code Scanning
- Azure DevOps
- Visual Studio
- Many other tools

### JUnit XML

Test report format for CI/CD integration:
```bash
iltero scan static --path . --format junit --output results.xml
```

Displays violations as failed tests in:
- Jenkins
- GitLab CI
- CircleCI
- Azure Pipelines
- Most CI/CD platforms

---

## Best Practices

### Pre-Commit Scanning

Run scans before committing code:

```bash
# Add to .git/hooks/pre-commit
#!/bin/bash
iltero scan static --path . --fail-on high
```

### Pull Request Scanning

Scan changed files in pull requests:

```bash
# In CI/CD pipeline
git diff --name-only origin/main... | grep '\.tf$' > changed-files.txt

if [ -s changed-files.txt ]; then
  iltero scan static --path . --fail-on high
fi
```

### Progressive Enforcement

Start with warnings, then enforce:

```bash
# Week 1: Just report
iltero scan static --path .

# Week 2: Fail on critical only
iltero scan static --path . --fail-on critical

# Week 3: Fail on high and critical
iltero scan static --path . --fail-on high

# Week 4: Fail on medium and above
iltero scan static --path . --fail-on medium
```

### Scan Result Storage

```bash
# Store scan results for historical analysis
iltero scan static \
  --path . \
  --upload \
  --stack-id stk_abc123

# Query historical scans
iltero compliance violations list --stack-id stk_abc123
```

---

## Troubleshooting

### Scanner Not Found

```bash
# Check scanner installation
iltero scanner check

# Install missing scanners
pip install checkov
brew install opa  # macOS
pip install c7n   # Cloud Custodian
```

### Scan Timeout

```bash
# Increase scan timeout (default: 300 seconds)
export ILTERO_SCAN_TIMEOUT=600

iltero scan static --path ./large-repo
```

### False Positives

```bash
# Suppress specific violations
# Create .iltero-ignore file in repo root

# Suppress by rule ID
CKV_AWS_19

# Suppress by file pattern
modules/legacy/*.tf

# Then re-scan
iltero scan static --path .
```

### Upload Failures

```bash
# Verify authentication
iltero auth status

# Verify stack exists
iltero stack get stk_abc123

# Check network connectivity
curl -I https://api.iltero.io

# Retry upload
iltero scan static \
  --path . \
  --stack-id stk_abc123 \
  --upload
```

---

## See Also

- [Scanner Commands](scanner.md) - Manage scanner installation
- [Compliance Commands](compliance.md) - View compliance violations
- [Stack Commands](stack.md) - Associate scans with stacks
- [CI/CD Integration](../ci-cd/README.md) - Integrate scans into pipelines

---

**Next Steps:**
- [Check scanner installation](scanner.md)
- [View compliance violations](compliance.md)
- [Set up CI/CD scanning](../ci-cd/github-actions.md)
