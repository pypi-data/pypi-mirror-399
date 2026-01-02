# End-to-End Testing Guide

## Overview

This directory contains **real E2E tests** that execute against a live Iltero backend instance with actual scanners and Terraform projects.

## Key Differences

| Type | Location | Backend | Scanners | Purpose |
|------|----------|---------|----------|---------|
| **Unit Tests** | `tests/unit/` | Mocked | Mocked | Test individual components |
| **Integration Tests** | `tests/integration/` | Mocked | Mocked | Test CLI commands work together |
| **E2E Tests** | `tests/e2e/` | **Real** | **Real** | Test full workflows end-to-end |

## Prerequisites

### 1. Backend Access
- Access to a test/staging Iltero backend
- Valid authentication token

### 2. Scanners Installed
```bash
# Install Checkov
pip install checkov

# Install OPA
brew install opa  # macOS
# or
curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_darwin_amd64
chmod +x opa
sudo mv opa /usr/local/bin/

# Verify installation
checkov --version
opa version
```

### 3. Terraform (Optional - for plan workflow tests)
```bash
brew install terraform  # macOS
terraform --version
```

## Running E2E Tests

### Basic E2E Test Run
```bash
# With token from environment
export ILTERO_TEST_TOKEN="itk_your_test_token"
pytest tests/e2e/ --e2e

# With token as argument
pytest tests/e2e/ --e2e --test-token="itk_your_test_token"
```

### Specify Backend URL
```bash
# Default: https://staging.iltero.com
export ILTERO_BACKEND_URL="https://test.iltero.com"
pytest tests/e2e/ --e2e --backend-url="https://test.iltero.com"
```

### Run Specific Test Classes
```bash
# Test only authentication
pytest tests/e2e/test_real_workflows.py::TestRealAuthentication --e2e

# Test only scanning
pytest tests/e2e/test_real_workflows.py::TestRealScanning --e2e

# Test full CI/CD pipeline
pytest tests/e2e/test_real_workflows.py::TestRealCICDWorkflow --e2e
```

### Run with Verbose Output
```bash
pytest tests/e2e/ --e2e -v -s
```

## Test Coverage

### TestRealAuthentication
- `test_auth_whoami` - Verify authentication with real backend

### TestRealScanning  
- `test_scanner_check_real` - Verify scanners are installed
- `test_static_scan_real_project` - Scan real Terraform with real scanners
- `test_static_scan_with_real_upload` - Upload scan results to backend

### TestRealWorkspaceManagement
- `test_workspace_list_real` - List workspaces from real backend

### TestRealCICDWorkflow
- `test_full_cicd_pipeline` - Complete validate → plan → evaluation workflow

### TestRealOutputFormats
- `test_sarif_output_real` - Generate real SARIF output
- `test_junit_output_real` - Generate real JUnit XML output

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ILTERO_TEST_TOKEN` | **Yes** | - | Authentication token for API |
| `ILTERO_BACKEND_URL` | No | `https://staging.iltero.com` | Backend URL |
| `ILTERO_TEST_STACK_ID` | No (for upload tests) | - | Stack ID for webhook tests |

## Example CI/CD Integration

### GitHub Actions
```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install checkov
          pip install opa
          pip install -e .
      
      - name: Run E2E tests
        env:
          ILTERO_TEST_TOKEN: ${{ secrets.ILTERO_TEST_TOKEN }}
          ILTERO_BACKEND_URL: https://staging.iltero.com
        run: |
          pytest tests/e2e/ --e2e -v
```

## Skipping E2E Tests

By default, E2E tests are **skipped** unless you provide the `--e2e` flag:

```bash
# This will skip E2E tests
pytest tests/

# This will run E2E tests
pytest tests/ --e2e
```

## Test Data

E2E tests create temporary Terraform projects with:
- Real AWS resource definitions
- Intentional policy violations (for testing)
- Proper Terraform structure

**Note:** Tests do NOT actually deploy resources - they only scan and plan.

## Troubleshooting

### "Backend not available"
```bash
# Check connectivity
curl https://staging.iltero.com/health

# Verify backend URL
echo $ILTERO_BACKEND_URL
```

### "Scanners not installed"
```bash
# Check scanner availability
which checkov
which opa

# Verify versions
checkov --version
opa version
```

### "Authentication failed"
```bash
# Verify token format
echo $ILTERO_TEST_TOKEN | grep "^itk_"

# Test token manually
curl -H "Authorization: Bearer $ILTERO_TEST_TOKEN" \
  https://staging.iltero.com/api/auth/session
```

## Best Practices

1. **Use staging/test environment** - Never run E2E tests against production
2. **Clean up test data** - Tests should not leave artifacts in backend
3. **Idempotent tests** - Tests should be repeatable without side effects
4. **Fast feedback** - Keep E2E tests focused and fast (< 5 min total)
5. **CI/CD integration** - Run E2E tests in CI pipeline before deployment
