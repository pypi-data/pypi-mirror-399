# Contributing to Iltero CLI

Thank you for your interest in contributing to the Iltero CLI! We welcome contributions from the community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Developer Certificate of Origin](#developer-certificate-of-origin)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/iltero-cli.git
   cd iltero-cli
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/iltero/iltero-cli.git
   ```

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Git
- A GitHub account

### Install Development Dependencies

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package with development dependencies
pip install -e ".[dev]"
```

### Verify Installation

```bash
# Run tests
pytest

# Check CLI works
iltero --version
```

## Making Changes

### Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

**Branch Naming Convention:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test improvements

### Commit Messages

Write clear, concise commit messages following this format:

```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting (no functional changes)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Example:**
```
feat: add workspace list command

Implement `iltero workspace list` to display all workspaces
in the current organization. Includes filtering by environment
and output formatting options.

Closes #123
```

## Developer Certificate of Origin

By contributing to this project, you certify that:

1. The contribution was created in whole or in part by you and you have the right to submit it under the Apache 2.0 license.
2. The contribution is based upon previous work that, to the best of your knowledge, is covered under an appropriate open source license and you have the right under that license to submit that work with modifications.
3. The contribution was provided directly to you by some other person who certified (1) or (2) and you have not modified it.
4. You understand and agree that this project and the contribution are public and that a record of the contribution is maintained indefinitely.

### Sign Your Commits

All commits must be signed off using the Developer Certificate of Origin (DCO). This is done by adding a `Signed-off-by` line to your commit messages:

```bash
git commit -s -m "feat: add new feature"
```

This adds:
```
Signed-off-by: Your Name <your.email@example.com>
```

**Configure Git for DCO:**
```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

**Note:** We use DCO instead of a Contributor License Agreement (CLA) to reduce friction for contributors while maintaining legal clarity.

## Pull Request Process

### Before Submitting

1. **Sync with upstream:**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests:**
   ```bash
   pytest
   ```

3. **Run linting:**
   ```bash
   ruff check .
   mypy iltero
   ```

4. **Update documentation** if needed

5. **Ensure all commits are signed off** (DCO)

### Submitting the PR

1. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Open a Pull Request on GitHub

3. Fill out the PR template with:
   - **Description** of the change
   - **Related issues** (e.g., "Closes #123")
   - **Testing** performed
   - **Screenshots** (if UI changes)

### PR Review Process

- A maintainer will review your PR within 3-5 business days
- Address review feedback by pushing new commits
- Once approved, a maintainer will merge your PR
- Your contribution will be included in the next release

### PR Checklist

- [ ] Code follows the project's coding standards
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] All commits are signed off (DCO)
- [ ] PR title is clear and descriptive
- [ ] Related issues are linked

## Coding Standards

### Python Style

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length**: 100 characters (not 79)
- **Quotes**: Double quotes preferred
- **Type hints**: Required for all functions
- **Docstrings**: Google style

### Code Quality Tools

We use:
- **ruff**: Fast Python linter
- **mypy**: Static type checker
- **pytest**: Testing framework

### Type Hints

All functions must have type hints:

```python
def create_workspace(name: str, org_id: str) -> Workspace:
    """Create a new workspace.
    
    Args:
        name: Workspace name
        org_id: Organization ID
        
    Returns:
        Created workspace object
        
    Raises:
        ValidationError: If name is invalid
        APIError: If creation fails
    """
    pass
```

### Error Handling

Use custom exceptions from `iltero.core.exceptions`:

```python
from iltero.core.exceptions import ValidationError, APIError

if not is_valid_name(name):
    raise ValidationError(f"Invalid workspace name: {name}")
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=iltero --cov-report=html

# Run specific test file
pytest tests/unit/test_config.py

# Run specific test
pytest tests/unit/test_config.py::test_config_from_env
```

### Writing Tests

- Place tests in `tests/unit/` or `tests/integration/`
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive test names

**Example:**

```python
def test_workspace_list_filters_by_environment(mock_api_client):
    """Test that workspace list correctly filters by environment."""
    # Arrange
    client = WorkspaceClient(mock_api_client)
    
    # Act
    workspaces = client.list(environment="production")
    
    # Assert
    assert all(w.environment == "production" for w in workspaces)
```

### Test Coverage

- Aim for 80%+ coverage on core modules
- 100% coverage on critical paths (auth, API client)
- Command-level tests can be integration tests

## Documentation

### Docstrings

Use Google-style docstrings:

```python
def calculate_total(items: list[Item], tax_rate: float = 0.0) -> Decimal:
    """Calculate total cost including tax.
    
    Args:
        items: List of items to sum
        tax_rate: Tax rate as decimal (e.g., 0.08 for 8%)
        
    Returns:
        Total cost including tax
        
    Raises:
        ValueError: If tax_rate is negative
        
    Example:
        >>> items = [Item(price=10.0), Item(price=20.0)]
        >>> calculate_total(items, tax_rate=0.08)
        Decimal('32.40')
    """
    pass
```

### README Updates

Update the README when:
- Adding new commands
- Changing installation process
- Adding new features
- Changing configuration options

### Architecture Documentation

For significant changes, update documentation in `implementation_docs/`.

## What to Contribute

### Good First Issues

Look for issues labeled `good-first-issue` - these are ideal for first-time contributors.

### Ideas for Contributions

- **Bug fixes**: Check open issues
- **New commands**: Workspace, environment, policy management
- **Output formatters**: JSON, YAML, table improvements
- **Testing**: Increase test coverage
- **Documentation**: Improve guides, add examples
- **Error messages**: Make them more helpful

### What We Don't Accept

- Changes without tests
- Breaking changes without discussion
- Code that doesn't follow style guidelines
- Unsigned commits (missing DCO)

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue
- **Security**: Email security@iltero.com (see [SECURITY.md](SECURITY.md))

## Recognition

Contributors will be:
- Listed in release notes
- Credited in commit history
- Mentioned in the README (for significant contributions)

Thank you for contributing to Iltero CLI! 🎉

---

**Last Updated**: November 27, 2025
