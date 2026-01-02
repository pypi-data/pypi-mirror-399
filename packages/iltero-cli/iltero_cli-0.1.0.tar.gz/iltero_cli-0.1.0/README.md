# Iltero CLI

**Unified command-line interface for the Iltero platform**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)

## Overview

The Iltero CLI provides comprehensive access to all backend services through a terminal interface, following AWS CLI patterns for familiarity and ease of use.

## Features

- 🔐 **Token-based authentication** - Secure API token management
- 🎯 **Context-aware** - Maintain organization/workspace/environment context
- 📊 **Rich output** - Beautiful tables or JSON/YAML for scripting
- 🚀 **CI/CD optimized** - Environment variable configuration for pipelines
- 🔍 **Local scanning** - Checkov and OPA integration for compliance
- 🌐 **Complete platform access** - Workspaces, stacks, compliance, deployments

## Installation

### From PyPI (when published)

```bash
pip install iltero-cli
```

### From Source

```bash
git clone https://github.com/iltero/iltero-cli.git
cd iltero-cli
pip install -e .
```

### For Development

```bash
git clone https://github.com/iltero/iltero-cli.git
cd iltero-cli
pip install -e ".[dev]"
```

## Quick Start

### 1. Install the CLI

```bash
pip install iltero-cli
```

### 2. Configure Authentication

Get your API token from the [Iltero web UI](https://app.iltero.io), then:

```bash
# Interactive mode (stores in system keyring)
iltero auth set-token

# Or set environment variable (CI/CD mode)
export ILTERO_TOKEN=itk_u_your_token_here
```

### 3. Verify Authentication

```bash
iltero auth status
# ✓ Authenticated as: john.doe@company.com
```

### 4. Start Using the CLI

```bash
# List workspaces
iltero workspace list

# Create a stack
iltero stack create --name my-stack --workspace my-workspace

# Run compliance scan
iltero scan static --path ./terraform

# View violations
iltero compliance violations list --severity critical
```

📚 **See the [Quickstart Guide](docs/01-quickstart.md) for detailed instructions.**

## Configuration

The CLI can be configured via:

1. **Environment variables** (highest priority)
2. **Config file** (`~/.iltero/config.yaml`)
3. **Defaults** (lowest priority)

### Environment Variables

```bash
export ILTERO_TOKEN=itk_u_your_token          # API token
export ILTERO_API_URL=https://api.iltero.io  # Backend URL
export ILTERO_OUTPUT_FORMAT=json              # Output format (table, json, yaml)
export ILTERO_DEBUG=true                      # Enable debug logging
```

## Command Groups

- `iltero auth` - Authentication management
- `iltero token` - Token operations
- `iltero workspace` - Workspace management
- `iltero environment` - Environment operations
- `iltero stack` - Stack lifecycle
- `iltero scan` - Local compliance scanning
- `iltero compliance` - Compliance & violations
- `iltero repository` - Git integration
- `iltero deployment` - Deployment management
- `iltero registry` - Module & template registry
- `iltero org` - Organization management
- `iltero user` - User operations

## Development

### Setup Development Environment

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=iltero --cov-report=html

# Run specific test file
pytest tests/unit/test_auth.py
```

### Code Quality

```bash
# Format code
black iltero tests

# Lint code
ruff check iltero tests

# Type checking
mypy iltero
```

## Documentation

### User Documentation

- **[Documentation Home](docs/README.md)** - Complete documentation index
- **[Quickstart Guide](docs/01-quickstart.md)** - Get started in 5 minutes
- **[Installation Guide](docs/02-installation.md)** - Install on all platforms
- **[Configuration Guide](docs/03-configuration.md)** - Configure the CLI
- **[Command Reference](docs/commands/index.md)** - Complete command documentation
- **[CI/CD Integration](docs/ci-cd/README.md)** - GitHub Actions, GitLab CI, Jenkins, etc.
- **[Shell Completions](docs/06-shell-completions.md)** - Enable tab completion
- **[Troubleshooting Guide](docs/04-troubleshooting.md)** - Common issues and solutions

### Developer Documentation

- **[Developer Guide](docs/05-developer-guide.md)** - Development setup and workflows
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute
- **[Code of Conduct](CODE_OF_CONDUCT.md)** - Community guidelines
- **[Security Policy](SECURITY.md)** - Security vulnerability reporting

## Trademark Notice

"Iltero" and the Iltero logo are trademarks of Iltero Team. Use of these trademarks is subject to the [Trademark Policy](TRADEMARK_POLICY.md).

You may:
- Use the Iltero name to refer to this project in articles, tutorials, and documentation
- State compatibility with Iltero (e.g., "works with Iltero")
- Fork this project with a different name

You may not:
- Use "Iltero" in your project name for forks or derivative works
- Use the Iltero logo in ways that suggest endorsement
- Create confusion about official vs. unofficial projects

For questions about trademark usage, contact: legal@iltero.com

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

By contributing, you agree to the [Developer Certificate of Origin (DCO)](https://developercertificate.org/). All commits must be signed off (`git commit -s`).

## Security

To report security vulnerabilities, please see [SECURITY.md](SECURITY.md).

## Support

- Issues: https://github.com/iltero/iltero-cli/issues
- Documentation: https://docs.iltero.io/cli
- Website: https://iltero.io
