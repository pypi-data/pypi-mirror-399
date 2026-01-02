# CI/CD Integration

Complete guide for integrating Iltero CLI into your CI/CD pipelines.

## Overview

Iltero CLI is designed for seamless CI/CD integration with:

- **Environment variable configuration** - No interactive prompts required
- **Pipeline tokens** - Dedicated tokens for automation (`itk_p_*`)
- **Standard exit codes** - Easy pass/fail determination
- **Multiple output formats** - JSON, SARIF, JUnit XML
- **Threshold configuration** - Fail builds based on severity levels

## Platform-Specific Guides

Choose your CI/CD platform:

- **[GitHub Actions](01-github-actions.md)** - Complete GitHub Actions integration with workflows
- **[GitLab CI](02-gitlab-ci.md)** - GitLab CI/CD pipeline configuration
- **[Jenkins](03-jenkins.md)** - Jenkins declarative and scripted pipelines
- **[Azure DevOps](04-azure-devops.md)** - Azure Pipelines integration
- **[CircleCI](05-circleci.md)** - CircleCI configuration
- **[Bitbucket Pipelines](06-bitbucket-pipelines.md)** - Bitbucket Pipelines setup

## Quick Start

### 1. Create Pipeline Token

```bash
iltero token create --name "CI/CD Pipeline" --type pipeline
```

Copy the token (starts with `itk_p_`) - you'll only see it once!

### 2. Add Secret to CI/CD Platform

| Platform | Secret Name | Location |
|----------|-------------|----------|
| GitHub Actions | `ILTERO_PIPELINE_TOKEN` | Repository Settings → Secrets |
| GitLab CI | `ILTERO_PIPELINE_TOKEN` | Project Settings → CI/CD → Variables |
| Jenkins | `iltero-pipeline-token` | Credentials Manager |
| Azure DevOps | `ILTERO_PIPELINE_TOKEN` | Pipeline Variables |
| CircleCI | `ILTERO_PIPELINE_TOKEN` | Project Settings → Environment Variables |
| Bitbucket | `ILTERO_PIPELINE_TOKEN` | Repository Settings → Pipelines → Variables |

### 3. Basic Pipeline Example

```bash
# Install CLI
pip install iltero-cli

# Authenticate
export ILTERO_TOKEN=$PIPELINE_TOKEN

# Run scan
iltero scan static --path ./terraform --format json

# Fail on critical violations
iltero scan static --path ./terraform --fail-on critical
```

## Common Workflows

### Pre-Commit Validation

Run scans before merging code:

```yaml
on: pull_request

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install iltero-cli checkov
      - run: iltero scan static --path . --fail-on high
        env:
          ILTERO_TOKEN: ${{ secrets.ILTERO_PIPELINE_TOKEN }}
```

### Post-Merge Scanning

Upload scan results after merging to main:

```yaml
on:
  push:
    branches: [main]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install iltero-cli checkov
      - run: |
          iltero scan static \
            --path . \
            --stack-id $STACK_ID \
            --upload
        env:
          ILTERO_TOKEN: ${{ secrets.ILTERO_PIPELINE_TOKEN }}
```

### Security Scanning Integration

Upload results to security platforms:

```yaml
- run: iltero scan static --path . --format sarif --output results.sarif
  env:
    ILTERO_TOKEN: ${{ secrets.ILTERO_PIPELINE_TOKEN }}

- uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: results.sarif
```

## Environment Variables

Configure Iltero CLI via environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `ILTERO_TOKEN` | Pipeline token | Yes |
| `ILTERO_API_URL` | Backend API URL | No (defaults to production) |
| `ILTERO_OUTPUT_FORMAT` | Default output format | No (defaults to `table`) |
| `ILTERO_NO_COLOR` | Disable colored output | No (recommended for CI/CD) |
| `ILTERO_DEBUG` | Enable debug logging | No |
| `ILTERO_SCAN_TIMEOUT` | Scanner timeout in seconds | No (defaults to 300) |
| `ILTERO_REQUEST_TIMEOUT` | HTTP request timeout | No (defaults to 30) |

**Example:**
```yaml
env:
  ILTERO_TOKEN: ${{ secrets.ILTERO_PIPELINE_TOKEN }}
  ILTERO_OUTPUT_FORMAT: json
  ILTERO_NO_COLOR: true
```

## Output Formats

### JSON (Default for automation)

```bash
iltero scan static --path . --format json --output results.json
```

Parse results:
```bash
CRITICAL=$(jq '.summary.critical // 0' results.json)
if [ "$CRITICAL" -gt 0 ]; then
  echo "Found $CRITICAL critical violations"
  exit 1
fi
```

### SARIF (GitHub Security, Azure DevOps)

```bash
iltero scan static --path . --format sarif --output results.sarif
```

Upload to GitHub:
```yaml
- uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: results.sarif
```

### JUnit XML (Test Reports)

```bash
iltero scan static --path . --format junit --output results.xml
```

Display as test results in most CI/CD platforms.

## Best Practices

### 1. Use Pipeline Tokens

✅ Create dedicated pipeline tokens (`itk_p_*`)  
❌ Don't use personal tokens (`itk_u_*`) in CI/CD

### 2. Set Failure Thresholds

```bash
# Fail immediately on critical
iltero scan static --path . --fail-on critical

# Or check manually
if [ "$CRITICAL_COUNT" -gt 0 ]; then exit 1; fi
```

### 3. Cache Dependencies

```yaml
# GitHub Actions
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip
```

### 4. Verify Installation

```bash
# Always verify CLI and scanners are available
iltero --version
iltero scanner check
iltero auth status
```

### 5. Store Artifacts

```yaml
# Keep scan results for auditing
- uses: actions/upload-artifact@v3
  if: always()
  with:
    name: scan-results
    path: results.json
```

### 6. Progressive Enforcement

Start lenient, then tighten:

```bash
# Week 1: Just report
iltero scan static --path .

# Week 2: Fail on critical
iltero scan static --path . --fail-on critical

# Week 3: Fail on high+
iltero scan static --path . --fail-on high
```

## Troubleshooting

### Authentication Fails

```bash
# Debug authentication
iltero --debug auth status

# Verify token is set
echo "Token: ${ILTERO_TOKEN:0:10}..."

# Check token format (should start with itk_p_)
echo "$ILTERO_TOKEN" | grep -q "^itk_p_"
```

### Scanner Not Found

```bash
# Check scanner installation
iltero scanner check

# Install missing scanners
pip install checkov
```

### Timeout Issues

```bash
# Increase timeouts
export ILTERO_SCAN_TIMEOUT=600
export ILTERO_REQUEST_TIMEOUT=60
```

### Output Issues

```bash
# Disable colors (CI/CD logs)
export ILTERO_NO_COLOR=true

# Use JSON for parsing
export ILTERO_OUTPUT_FORMAT=json
```

## Example Patterns

### Fail on Critical Violations

```bash
iltero scan static \
  --path . \
  --format json \
  --output results.json

CRITICAL=$(jq '.summary.critical // 0' results.json)
if [ "$CRITICAL" -gt 0 ]; then
  echo "::error::Found $CRITICAL critical violations"
  exit 1
fi
```

### Multi-Environment Scanning

```yaml
strategy:
  matrix:
    environment: [dev, staging, prod]

steps:
  - run: |
      iltero scan static \
        --path ./envs/${{ matrix.environment }} \
        --stack-id ${{ vars[format('STACK_{0}', matrix.environment)] }} \
        --upload
```

### Conditional Upload

```bash
# Only upload on main branch
if [ "$BRANCH" = "main" ]; then
  iltero scan static \
    --path . \
    --stack-id $STACK_ID \
    --upload
else
  iltero scan static --path .
fi
```

## Platform Comparison

| Feature | GitHub Actions | GitLab CI | Jenkins | Azure DevOps | CircleCI | Bitbucket |
|---------|----------------|-----------|---------|--------------|----------|-----------|
| YAML Config | ✅ | ✅ | ❌ (Groovy) | ✅ | ✅ | ✅ |
| SARIF Upload | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Artifact Storage | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Matrix Builds | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Secrets Mgmt | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

## Next Steps

1. **Choose your platform** from the guides above
2. **Create pipeline token** - `iltero token create --type pipeline`
3. **Add token to secrets** in your CI/CD platform
4. **Copy example workflow** from platform-specific guide
5. **Test in PR** before deploying to main branch

## See Also

- [Token Commands](../commands/token.md) - Create pipeline tokens
- [Scan Commands](../commands/scan.md) - Scanning reference
- [Configuration Guide](../configuration.md) - CLI configuration
- [Troubleshooting Guide](../troubleshooting.md) - Common issues

---

**Get Started:**
- [GitHub Actions →](github-actions.md)
- [GitLab CI →](gitlab-ci.md)
- [Jenkins →](jenkins.md)
