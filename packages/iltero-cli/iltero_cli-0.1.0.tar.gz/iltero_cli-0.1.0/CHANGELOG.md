# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-12-29

### Added

#### Core Commands
- **Workspace Management** - Create, list, select, and manage workspaces
- **Environment Management** - Full environment lifecycle operations
- **Stack Management** - Stack creation, configuration, and monitoring
  - Stack runs, variables, drift detection
  - Stack approvals and exceptions
  - Policy overrides and configuration
- **Compliance Scanning** - Multi-phase security scanning
  - Static code scanning (pre-plan)
  - Policy evaluation (post-plan)
  - Runtime scanning (post-apply)
  - Support for Checkov, OPA, and Cloud Custodian scanners
- **Scanner Management** - Check scanner availability and versions
- **Authentication** - Token-based auth with keyring support
- **Configuration** - Flexible config management (file, env vars, CLI flags)

#### CI/CD Integration
- GitHub Actions workflow examples
- GitLab CI integration guide
- Jenkins pipeline templates
- Azure DevOps integration
- CircleCI configuration
- Bitbucket Pipelines support
- Automatic CI/CD environment detection

#### Output Formats
- Table output (default, rich formatting)
- JSON output (for parsing)
- YAML output (for human reading)
- SARIF output (for GitHub Security)
- JUnit XML output (for test reporting)

#### Compliance Features
- Compliance violations tracking
- Compliance scans management
- Compliance reports generation
- Policy resolution with provenance
- Evidence collection and submission

#### Registry & Templates
- Template bundle discovery from marketplace
- Template bundle validation
- Bootstrap with compliance templates
- Cross-unit dependency analysis
- Private registry module management

#### Repository Management
- Repository listing and details
- Repository creation and sync
- CI/CD initialization for repositories

#### Organization & User Management
- Organization settings management
- User and team management
- Service account operations
- Access control configuration

#### Developer Experience
- Rich terminal output with colors and tables
- Progress indicators for long operations
- Comprehensive error messages
- Shell completions (Bash, Zsh, Fish)
- Flexible configuration precedence (env > config > defaults)
- Secure credential storage via system keyring
- Context management for workspace/environment selection

### Quality Assurance
- 720 automated tests (675 unit + 45 integration)
- 31% code coverage (focused on business logic)
- Type hints throughout codebase
- Comprehensive API client integration
- CI/CD pipeline with quality gates
- Pre-commit hooks for code quality

### Documentation
- Complete command reference (15 command groups)
- Installation guide (pip, pipx, source)
- Configuration guide (all options documented)
- Troubleshooting guide
- Developer guide (setup, testing, contributing)
- CI/CD integration guides (6 platforms)
- Shell completion installation guide
- Packaging and release documentation
- Versioning strategy documented

### Infrastructure
- GitHub Actions CI/CD workflow
  - Multi-platform testing (Ubuntu, macOS, Windows)
  - Multi-Python version testing (3.11, 3.12)
  - Code quality checks (Ruff, Black, MyPy)
  - Security scanning (Bandit, Safety, pip-audit)
  - Coverage reporting (Codecov integration)
- Pre-commit hooks configuration
- Package distribution (PyPI wheel + source)
- Automated testing and validation

### Dependencies
- Python 3.11+ required
- Typer for CLI framework
- Rich for terminal output
- httpx for HTTP client
- Pydantic for data validation
- Keyring for credential storage
- Optional: Checkov, OPA, Cloud Custodian for scanning

### Notes
- This is the initial **0.1.0** release following [semantic versioning](https://semver.org/)
- The API is **not yet stable** during the 0.x series
- Breaking changes may occur in minor versions during 0.x phase
- Feedback and bug reports welcome as we stabilize the API

[0.1.0]: https://github.com/iltero-io/iltero-cli/releases/tag/v0.1.0
