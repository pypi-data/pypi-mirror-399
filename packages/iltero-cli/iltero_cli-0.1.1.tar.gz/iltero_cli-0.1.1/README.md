# Iltero CLI

**Command-line interface for the Iltero platform**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/iltero-cli.svg)](https://pypi.org/project/iltero-cli/)

## Installation

```bash
pip install iltero-cli
```

**Requirements:** Python 3.11 or higher

## Quick Start

### 1. Configure Authentication

Get your API token from the Iltero platform, then:

```bash
# Set your token (stored securely in system keyring)
iltero auth set-token

# Or use environment variable
export ILTERO_TOKEN=itk_u_your_token_here
```

### 2. Verify Connection

```bash
iltero auth status
```

### 3. Basic Usage

```bash
# List workspaces
iltero workspace list

# Create a stack
iltero stack create --name my-stack --workspace my-workspace

# Run compliance scan
iltero scan static --path ./terraform

# View help
iltero --help
```

## Configuration

Configure via environment variables or config file (`~/.iltero/config.yaml`):

```bash
export ILTERO_TOKEN=itk_u_your_token          # API token (required)
export ILTERO_API_URL=https://api.iltero.io  # Backend URL
export ILTERO_OUTPUT_FORMAT=json              # Output format: table, json, yaml
```

## Available Commands

- `iltero auth` - Authentication management
- `iltero workspace` - Workspace operations
- `iltero environment` - Environment management
- `iltero stack` - Stack lifecycle operations
- `iltero scan` - Local compliance scanning
- `iltero compliance` - Compliance and violations
- `iltero registry` - Module and template registry
- `iltero token` - Token management

Run `iltero <command> --help` for detailed command documentation.

## Support

- **Documentation**: https://docs.iltero.io/cli
- **Website**: https://iltero.io

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.
