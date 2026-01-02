# CI/CD Pipeline

Automated continuous integration and deployment pipeline for the Iltero CLI.

## Overview

The CI/CD pipeline runs on every push and pull request, ensuring code quality, security, and functionality across multiple platforms and Python versions.

## Pipeline Jobs

### 1. Code Quality
**Purpose:** Ensure code meets quality standards

**Checks:**
- **Ruff Linter** - Fast Python linter (replaces Flake8, isort, etc.)
- **Ruff Formatter** - Code formatting verification
- **Black** - Python code formatter (double-check)
- **MyPy** - Static type checking

**Trigger:** All commits and PRs

### 2. Security Scanning
**Purpose:** Identify security vulnerabilities

**Tools:**
- **Bandit** - Python security issue scanner
  - Scans for common security issues
  - Generates JSON report artifact
- **Safety** - Dependency vulnerability checker
  - Checks for known CVEs in dependencies
- **pip-audit** - Comprehensive dependency audit
  - Audits all installed packages
  - Generates detailed JSON report

**Artifacts:**
- `bandit-report.json` (30 days retention)
- `pip-audit-report.json` (30 days retention)

### 3. Tests
**Purpose:** Verify functionality across platforms

**Matrix:**
- **Operating Systems:** Ubuntu, macOS, Windows
- **Python Versions:** 3.11, 3.12

**Tests:**
- Unit tests (with coverage)
- Integration tests
- Coverage reporting to Codecov

**Artifacts:**
- `coverage-report-{os}-py{version}` (30 days retention)

### 4. Build
**Purpose:** Verify package builds correctly

**Steps:**
1. Build package with PDM
2. Validate package with twine
3. Test installation in clean environment
4. Verify CLI works

**Artifacts:**
- `dist-packages` containing `.whl` and `.tar.gz` (30 days retention)

### 5. Documentation Lint
**Purpose:** Ensure documentation quality

**Checks:**
- Markdown formatting (markdownlint)
- Broken link detection
- Consistent formatting

### 6. Summary
**Purpose:** Aggregate results and determine CI status

**Logic:**
- ✅ Pass if: code-quality, tests, and build succeed
- ❌ Fail if: any critical job fails
- ⚠️ Warning if: security or docs jobs fail

## Pre-commit Hooks

Local code quality checks before committing.

### Setup

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

### Hooks Included

1. **General:**
   - Remove trailing whitespace
   - Fix end-of-file
   - Check YAML/JSON/TOML syntax
   - Detect large files (>1MB)
   - Detect private keys
   - Check for merge conflicts

2. **Python:**
   - Ruff linter (with auto-fix)
   - Ruff formatter
   - Black formatter
   - MyPy type checker
   - Bandit security scanner

3. **Documentation:**
   - Markdown linting

4. **Dependencies:**
   - Poetry/PDM validation

## Triggering the Pipeline

### Automatic Triggers

**Push to branches:**
```bash
git push origin main
git push origin develop
```

**Pull requests:**
```bash
# Create PR targeting main or develop
```

### Manual Trigger

```bash
# Via GitHub UI:
# Actions → CI → Run workflow
```

## Configuration Files

### Main Pipeline
**File:** `.github/workflows/ci.yml`

Key configurations:
- Python version: 3.11 (primary)
- Test matrix: Ubuntu/macOS/Windows × Python 3.11/3.12
- Artifact retention: 30 days

### Pre-commit
**File:** `.pre-commit-config.yaml`

Hook versions:
- Ruff: v0.8.4
- Black: 24.10.0
- MyPy: v1.13.0
- Bandit: 1.8.0

### Link Checking
**File:** `.github/markdown-link-check-config.json`

Settings:
- Timeout: 20s
- Retry on 429: Yes
- Retry count: 3
- Ignores: Internal Iltero URLs (not yet live)

### Security Scanning
**File:** `pyproject.toml` → `[tool.bandit]`

Settings:
- Excludes: tests/, .venv/, htmlcov/
- Skips: B101 (assert in tests), B601 (validated shell commands)

## Viewing Results

### GitHub Actions UI

1. Navigate to repository
2. Click "Actions" tab
3. Select workflow run
4. View job results and logs

### Artifacts

Download from workflow run:
- Coverage reports
- Security scan results
- Build packages

### Codecov

View coverage trends:
```
https://codecov.io/gh/iltero/iltero-cli
```

## CI/CD Best Practices

### Before Committing

```bash
# Run pre-commit checks
pre-commit run --all-files

# Run tests locally
pdm run pytest

# Check types
pdm run mypy iltero/
```

### Before Merging PR

- ✅ All CI jobs passing
- ✅ Code coverage maintained or improved
- ✅ No new security issues
- ✅ Documentation updated
- ✅ Changelog updated (if applicable)

### After Merging

- Monitor CI run on main branch
- Check for any platform-specific failures
- Review security scan results
- Verify build artifacts

## Troubleshooting

### CI Failures

**Code Quality:**
```bash
# Fix locally
pdm run ruff check --fix iltero/ tests/
pdm run black iltero/ tests/
```

**Type Errors:**
```bash
# Check types
pdm run mypy iltero/

# Add type ignores if necessary
# type: ignore[error-code]
```

**Test Failures:**
```bash
# Run failing test
pdm run pytest tests/path/to/test.py -v

# Run with debugging
pdm run pytest tests/path/to/test.py -vv -s
```

**Build Failures:**
```bash
# Clean and rebuild
rm -rf dist/
pdm build
```

### Pre-commit Issues

**Hooks not running:**
```bash
# Reinstall
pre-commit uninstall
pre-commit install
```

**Update hooks:**
```bash
pre-commit autoupdate
```

**Skip hooks (emergency only):**
```bash
git commit --no-verify -m "message"
```

## Secrets Configuration

Required secrets in GitHub repository settings:

| Secret | Purpose | Required |
|--------|---------|----------|
| `CODECOV_TOKEN` | Coverage reporting | Optional |
| `PYPI_TOKEN` | Publishing to PyPI | For releases |

**Setup:**
1. Go to Repository Settings → Secrets and variables → Actions
2. Add new repository secret
3. Name: `CODECOV_TOKEN` or `PYPI_TOKEN`
4. Value: Token from service
5. Save

## Future Enhancements

- [ ] Dependabot for automated dependency updates
- [ ] SAST scanning (CodeQL)
- [ ] Performance benchmarks
- [ ] Automatic release creation on tags
- [ ] Documentation deployment
- [ ] Container image builds

## See Also

- [Developer Guide](../docs/05-developer-guide.md)
- [Packaging Guide](../docs/07-packaging.md)
- [Contributing Guidelines](../CONTRIBUTING.md)
