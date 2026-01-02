# Compliance Commands

View and manage compliance violations.

## Overview

The `iltero compliance` command group helps you:
- View compliance violations from scans
- Filter violations by severity, status, workspace
- Mark violations as remediated
- View compliance dashboard

## Commands

### `iltero compliance violations list`

List compliance violations.

```bash
# List all violations
iltero compliance violations list

# Filter by severity
iltero compliance violations list --severity critical

# Filter by status
iltero compliance violations list --status open

# Filter by workspace
iltero compliance violations list --workspace production-infra
```

**Options:**
- `--severity SEVERITY` - Filter by severity: `critical`, `high`, `medium`, `low`, `info`
- `--status STATUS` - Filter by status: `open`, `remediated`, `suppressed`
- `--workspace WORKSPACE` - Filter by workspace
- `--stack-id STACK_ID` - Filter by stack
- `--output FORMAT` - Output format: `table`, `json`, `yaml`

**Example output:**
```
ID           Severity  Rule                    File                      Status
──────────────────────────────────────────────────────────────────────────────────
vio_abc123   CRITICAL  S3 bucket not encrypted modules/storage/s3.tf:15  Open
vio_def456   HIGH      SG allows 0.0.0.0/0     modules/network/sg.tf:8   Open
vio_ghi789   MEDIUM    IAM wildcard actions    modules/iam/policy.tf:22  Remediated
```

### `iltero compliance violations get`

Get detailed information about a specific violation.

```bash
iltero compliance violations get vio_abc123

# JSON output
iltero compliance violations get vio_abc123 --output json
```

**Example output:**
```
Violation: vio_abc123
Severity: CRITICAL
Status: Open

Rule: CKV_AWS_19
Description: S3 bucket not encrypted at rest
Category: Encryption

Location:
  File: modules/storage/s3.tf
  Line: 15-25
  
Stack: api-gateway (stk_xyz789)
Workspace: production-infra
Environment: production

Detected: 2024-12-04 10:30:00
Last Updated: 2024-12-04 10:30:00

Remediation:
  Enable encryption for S3 bucket using AWS KMS or S3 managed keys.
  
  Example:
    resource "aws_s3_bucket" "example" {
      bucket = "my-bucket"
      
      server_side_encryption_configuration {
        rule {
          apply_server_side_encryption_by_default {
            sse_algorithm = "AES256"
          }
        }
      }
    }
```

### `iltero compliance violations remediate`

Mark a violation as remediated.

```bash
iltero compliance violations remediate vio_abc123 \
  --note "Fixed in PR #456"

# Bulk remediate
iltero compliance violations remediate vio_abc123 vio_def456 \
  --note "Fixed encryption settings"
```

**Options:**
- `--note NOTE` - Remediation note explaining how the issue was fixed

### `iltero compliance dashboard`

View compliance dashboard for a workspace.

```bash
iltero compliance dashboard --workspace production-infra

# JSON output
iltero compliance dashboard --workspace production-infra --output json
```

**Example output:**
```
Compliance Dashboard: production-infra

Overview:
  Total Stacks: 12
  Total Violations: 45
  Open Violations: 38
  Remediated: 7

By Severity:
  Critical: 5  (11%)
  High: 12     (27%)
  Medium: 18   (40%)
  Low: 10      (22%)

Compliance Score: 73% (38 of 52 checks passed)

Top Violated Rules:
  1. CKV_AWS_19 - S3 bucket not encrypted (5 stacks)
  2. CKV_AWS_24 - Security group allows 0.0.0.0/0 (4 stacks)
  3. CKV_AWS_16 - RDS not encrypted (3 stacks)

Stacks with Most Violations:
  1. api-gateway (stk_xyz789) - 12 violations
  2. database (stk_abc123) - 8 violations
  3. networking (stk_def456) - 6 violations
```

## Workflow Examples

### Review and Remediate Violations

```bash
# 1. List critical violations
iltero compliance violations list --severity critical

# 2. Get details on each
iltero compliance violations get vio_abc123

# 3. Fix the issue in your code
# ... edit terraform files ...

# 4. Re-scan to verify fix
iltero scan static --path ./terraform --stack-id stk_xyz789 --upload

# 5. Mark as remediated
iltero compliance violations remediate vio_abc123 \
  --note "Enabled S3 encryption in commit abc123"
```

### Generate Compliance Report

```bash
# Export violations as JSON for reporting
iltero compliance violations list \
  --workspace production-infra \
  --output json > compliance-report.json

# Process with jq for custom reporting
jq '.violations | group_by(.severity)' compliance-report.json
```

### Track Compliance Over Time

```bash
# Weekly compliance check
iltero compliance dashboard --workspace production-infra --output json \
  > compliance-$(date +%Y-%m-%d).json

# Compare with previous week
# ... use diff or custom scripts ...
```

## Best Practices

### Prioritize by Severity

```bash
# Focus on critical first
iltero compliance violations list --severity critical --status open

# Then high
iltero compliance violations list --severity high --status open

# Then medium
iltero compliance violations list --severity medium --status open
```

### Team Assignments

```bash
# Export violations by category for team assignment
iltero compliance violations list --output json | \
  jq '.violations | group_by(.category)' > violations-by-category.json
```

### Track Remediation

```bash
# Always add meaningful notes
iltero compliance violations remediate vio_abc123 \
  --note "Added encryption in PR #456, reviewed by security team"
```

## See Also

- [Scan Commands](scan.md) - Run scans to detect violations
- [Stack Commands](stack.md) - Manage stacks with violations
- [CI/CD Integration](../ci-cd/README.md) - Automate compliance checking

---

**Next:** [Set up automated scanning](../ci-cd/github-actions.md)
