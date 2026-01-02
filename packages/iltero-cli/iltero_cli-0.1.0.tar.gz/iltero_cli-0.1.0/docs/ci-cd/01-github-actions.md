# GitHub Actions Integration

Complete guide for integrating Iltero CLI with GitHub Actions.

## Prerequisites

1. Create pipeline token: `iltero token create --type pipeline`
2. Add token to GitHub repository:
   - Go to **Settings** → **Secrets and variables** → **Actions**
   - Click **New repository secret**
   - Name: `ILTERO_PIPELINE_TOKEN`
   - Value: Your token (starts with `itk_p_`)

## Basic Workflow

Create `.github/workflows/iltero.yml`:

```yaml
name: Iltero Compliance

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  compliance-scan:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Iltero CLI
        run: pip install iltero-cli checkov
      
      - name: Run compliance scan
        env:
          ILTERO_TOKEN: ${{ secrets.ILTERO_PIPELINE_TOKEN }}
        run: |
          iltero scan static \
            --path ./terraform \
            --format json \
            --output scan-results.json
      
      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: scan-results
          path: scan-results.json
      
      - name: Check thresholds
        run: |
          CRITICAL=$(jq '.summary.critical // 0' scan-results.json)
          if [ "$CRITICAL" -gt 0 ]; then
            echo "❌ Found $CRITICAL critical violations"
            exit 1
          fi
```

## GitHub Code Scanning (SARIF)

Upload results to GitHub Security tab:

```yaml
name: Security Scan

on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - run: pip install iltero-cli checkov
      
      - name: Run scan
        env:
          ILTERO_TOKEN: ${{ secrets.ILTERO_PIPELINE_TOKEN }}
        run: iltero scan static --path . --format sarif --output iltero.sarif
      
      - name: Upload SARIF
        if: always()
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: iltero.sarif
```

## Multi-Environment Matrix

```yaml
name: Multi-Environment

on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        environment: [dev, staging, prod]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install iltero-cli checkov
      - run: |
          iltero scan static \
            --path ./envs/${{ matrix.environment }}
        env:
          ILTERO_TOKEN: ${{ secrets.ILTERO_PIPELINE_TOKEN }}
```

## See Also

- [CI/CD Overview](README.md)
- [Scan Commands](../commands/scan.md)
