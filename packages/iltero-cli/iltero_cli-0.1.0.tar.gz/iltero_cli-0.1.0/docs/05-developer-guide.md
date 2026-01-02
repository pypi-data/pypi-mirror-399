# Developer Guide

Complete guide for developers contributing to Iltero CLI.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Documentation](#documentation)
- [Release Process](#release-process)
- [Debugging](#debugging)

## Development Setup

### Prerequisites

- **Python 3.11+** - `python --version`
- **Git** - `git --version`
- **Make** (optional) - For automation tasks

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/iltero/iltero-cli.git
cd iltero-cli

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Verify installation
iltero --version
pytest --version
```

### Development Dependencies

The `[dev]` extra installs:

- **pytest** - Testing framework
- **pytest-cov** - Code coverage
- **pytest-mock** - Mocking utilities
- **black** - Code formatter
- **ruff** - Fast linter
- **mypy** - Type checker
- **pre-commit** - Git hooks
- **build** - Package builder
- **twine** - Package publisher

## Project Structure

```
iltero-cli/
├── iltero/                      # Main package
│   ├── __init__.py
│   ├── cli.py                   # CLI entry point
│   ├── version.py               # Version info
│   ├── commands/                # Command implementations
│   │   ├── auth/                # Authentication commands
│   │   ├── workspace/           # Workspace commands
│   │   ├── stack/               # Stack commands
│   │   ├── scan/                # Scanning commands
│   │   └── ...
│   ├── core/                    # Core functionality
│   │   ├── auth.py              # Authentication manager
│   │   ├── config.py            # Configuration manager
│   │   ├── context.py           # Context manager
│   │   ├── exceptions.py        # Custom exceptions
│   │   └── output.py            # Output formatting
│   ├── scanners/                # Scanner integrations
│   │   ├── checkov.py           # Checkov scanner
│   │   ├── opa.py               # OPA scanner
│   │   └── orchestrator.py     # Scanner orchestration
│   ├── custodian/               # Compliance & policy
│   └── utils/                   # Utility modules
├── tests/                       # Test suite
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── e2e/                     # End-to-end tests
├── docs/                        # Documentation
├── implementation_docs/         # Implementation notes
├── pyproject.toml               # Project metadata
├── README.md                    # Project README
└── CONTRIBUTING.md              # Contribution guide
```

### Key Modules

| Module | Purpose |
|--------|---------|
| `cli.py` | CLI entry point, command registration |
| `core/auth.py` | Token management, authentication |
| `core/config.py` | Configuration loading and management |
| `core/context.py` | Workspace/environment context |
| `core/output.py` | Table/JSON/YAML formatting |
| `scanners/orchestrator.py` | Scanner execution coordination |
| `commands/*` | Individual command implementations |

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/my-new-feature
```

### 2. Make Changes

Follow the [coding standards](#code-quality) and add tests for new features.

### 3. Run Tests Locally

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=iltero --cov-report=html

# Run specific test file
pytest tests/unit/core/test_auth.py

# Run specific test
pytest tests/unit/core/test_auth.py::test_token_validation
```

### 4. Format and Lint

```bash
# Format code
black iltero tests

# Lint code
ruff check iltero tests

# Type check
mypy iltero

# Or use pre-commit for all checks
pre-commit run --all-files
```

### 5. Commit Changes

```bash
# Sign-off required (DCO)
git commit -s -m "feat: add new awesome feature"
```

### 6. Push and Create PR

```bash
git push origin feature/my-new-feature
# Then create Pull Request on GitHub
```

## Testing

### Running Tests

```bash
# All tests (unit + integration)
pytest

# Only unit tests
pytest tests/unit/

# Only integration tests
pytest tests/integration/

# E2E tests (requires backend)
pytest tests/e2e/ --e2e --test-token=<token>

# Specific test file
pytest tests/unit/core/test_auth.py

# Specific test function
pytest tests/unit/core/test_auth.py::test_set_token

# With verbose output
pytest -v

# With debug output
pytest -vv -s
```

### Code Coverage

```bash
# Generate coverage report
pytest --cov=iltero --cov-report=html

# View report
open htmlcov/index.html

# Minimum coverage threshold
pytest --cov=iltero --cov-fail-under=80
```

### Writing Tests

#### Unit Test Example

```python
# tests/unit/core/test_auth.py
import pytest
from iltero.core.auth import AuthManager
from iltero.core.exceptions import AuthenticationError

def test_token_validation():
    """Test token format validation."""
    auth = AuthManager()
    
    # Valid tokens
    assert auth.validate_token_format("itk_u_abc123")
    assert auth.validate_token_format("itk_p_xyz789")
    
    # Invalid tokens
    assert not auth.validate_token_format("invalid")
    assert not auth.validate_token_format("")

def test_token_storage(tmp_path, mocker):
    """Test token storage in keyring."""
    # Mock keyring
    mock_keyring = mocker.patch("keyring.set_password")
    
    auth = AuthManager()
    auth.set_token("itk_u_test123")
    
    mock_keyring.assert_called_once_with(
        "iltero-cli", "api_token", "itk_u_test123"
    )
```

#### Integration Test Example

```python
# tests/integration/test_scan_workflow.py
import pytest
from typer.testing import CliRunner
from iltero.cli import app

runner = CliRunner()

def test_scan_workflow():
    """Test complete scan workflow."""
    # Run scan command
    result = runner.invoke(app, [
        "scan", "static",
        "--path", "./test-terraform",
        "--format", "json"
    ])
    
    assert result.exit_code == 0
    assert "violations" in result.stdout
```

#### E2E Test Example

```python
# tests/e2e/test_real_workflows.py
import pytest

@pytest.mark.e2e
def test_real_authentication(backend_url, test_token):
    """Test authentication against real backend."""
    from iltero.core.auth import AuthManager
    
    auth = AuthManager()
    auth.set_token(test_token)
    
    # Verify token works
    result = auth.verify_token()
    assert result["authenticated"] is True
```

### Test Markers

```python
# Unit test (default)
def test_something():
    pass

# Integration test
@pytest.mark.integration
def test_integration():
    pass

# E2E test (requires --e2e flag)
@pytest.mark.e2e
def test_e2e():
    pass

# Slow test
@pytest.mark.slow
def test_slow_operation():
    pass

# Skip test
@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass
```

## Code Quality

### Black (Code Formatting)

```bash
# Format all files
black iltero tests

# Check formatting without changes
black --check iltero tests

# Format specific file
black iltero/core/auth.py
```

**Configuration** in `pyproject.toml`:
```toml
[tool.black]
line-length = 100
target-version = ['py311']
```

### Ruff (Linting)

```bash
# Lint all files
ruff check iltero tests

# Auto-fix issues
ruff check --fix iltero tests

# Lint specific file
ruff check iltero/core/auth.py
```

**Configuration** in `pyproject.toml`:
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]  # Line too long (handled by black)
```

### Mypy (Type Checking)

```bash
# Type check all files
mypy iltero

# Type check specific file
mypy iltero/core/auth.py

# Strict mode
mypy --strict iltero
```

**Configuration** in `pyproject.toml`:
```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### Pre-commit Hooks

Automatically run checks before each commit:

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

**Configuration** in `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.9.1
    hooks:
      - id: black
  
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.5.0
    hooks:
      - id: ruff
        args: [--fix]
  
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def scan_directory(
    path: str,
    scanner: str = "checkov",
    upload: bool = False
) -> dict[str, Any]:
    """Scan a directory for compliance violations.
    
    Args:
        path: Path to directory to scan
        scanner: Scanner to use (checkov, opa, or all)
        upload: Whether to upload results to backend
    
    Returns:
        Scan results dictionary containing violations and summary
    
    Raises:
        ScannerNotFoundError: If scanner is not installed
        ScanTimeoutError: If scan exceeds timeout
    
    Example:
        >>> results = scan_directory("./terraform", scanner="checkov")
        >>> print(results["summary"]["total"])
        42
    """
    pass
```

### Adding Documentation

```bash
# Add to docs/ directory
docs/
├── GETTING_STARTED.md
├── COMMAND_REFERENCE.md
├── CONFIGURATION.md
└── TROUBLESHOOTING.md

# Update README.md for major changes

# Update CHANGELOG.md for all changes
```

## Debugging

### Enable Debug Mode

```bash
# Via flag
iltero --debug workspace list

# Via environment
export ILTERO_DEBUG=true
iltero workspace list

# With log file
export ILTERO_LOG_FILE=debug.log
iltero --debug workspace list
tail -f debug.log
```

### Using Python Debugger

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use breakpoint() (Python 3.7+)
breakpoint()

# Run test with debugger
pytest --pdb tests/unit/core/test_auth.py
```

### VS Code Debugging

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug CLI",
      "type": "python",
      "request": "launch",
      "module": "iltero.cli",
      "args": ["workspace", "list", "--debug"],
      "console": "integratedTerminal",
      "env": {
        "ILTERO_DEBUG": "true"
      }
    },
    {
      "name": "Debug Tests",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["-v", "tests/unit/"],
      "console": "integratedTerminal"
    }
  ]
}
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

def my_function():
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
```

## Release Process

### Version Bumping

```bash
# Update version in iltero/version.py
__version__ = "1.2.0"

# Update CHANGELOG.md
# Document all changes in this release

# Commit version bump
git commit -am "chore: bump version to 1.2.0"
```

### Creating a Release

```bash
# Create and push tag
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0

# Build package
python -m build

# Check package
twine check dist/*

# Upload to TestPyPI (optional)
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

### Release Checklist

- [ ] All tests passing
- [ ] Code coverage ≥ 80%
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in `version.py`
- [ ] Git tag created
- [ ] Package built and uploaded
- [ ] GitHub release created
- [ ] Release notes published

## Development Tips

### Useful Commands

```bash
# Run quick checks before committing
make check  # If Makefile exists
# or
black iltero tests && ruff check iltero tests && pytest

# Generate requirements.txt from pyproject.toml
pip-compile pyproject.toml

# Update dependencies
pip install --upgrade -e ".[dev]"

# Clean build artifacts
rm -rf build/ dist/ *.egg-info
find . -type d -name __pycache__ -exec rm -rf {} +
```

### Common Patterns

#### Adding a New Command

```python
# 1. Create command file: iltero/commands/mycommand/main.py
import typer

app = typer.Typer(help="My new command")

@app.command()
def list():
    """List items."""
    print("Listing items...")

# 2. Register in iltero/cli.py
from iltero.commands.mycommand import main as mycommand_cmd

app.add_typer(mycommand_cmd.app, name="mycommand")

# 3. Add tests: tests/unit/commands/test_mycommand.py
def test_mycommand_list():
    from typer.testing import CliRunner
    from iltero.cli import app
    
    runner = CliRunner()
    result = runner.invoke(app, ["mycommand", "list"])
    assert result.exit_code == 0
```

#### Using Configuration

```python
from iltero.core.config import ConfigManager

config = ConfigManager()
api_url = config.get("api_url")
timeout = config.get("request_timeout", default=30)
```

#### Using Authentication

```python
from iltero.core.auth import AuthManager

auth = AuthManager()
token = auth.get_token()
is_valid = auth.verify_token()
```

### VS Code Setup

Install recommended extensions:

- Python
- Pylance
- Black Formatter
- Ruff

Workspace settings (`.vscode/settings.json`):

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.linting.enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

## Getting Help

- **Documentation**: Read the guides in `docs/`
- **Issues**: Search [GitHub Issues](https://github.com/iltero/iltero-cli/issues)
- **Discussions**: Join [GitHub Discussions](https://github.com/iltero/iltero-cli/discussions)
- **Contributing**: See [CONTRIBUTING.md](../CONTRIBUTING.md)

## See Also

- [Contributing Guide](../CONTRIBUTING.md)
- [Code of Conduct](../CODE_OF_CONDUCT.md)
- [Getting Started Guide](GETTING_STARTED.md)
- [Testing Guide](../tests/README.md)
