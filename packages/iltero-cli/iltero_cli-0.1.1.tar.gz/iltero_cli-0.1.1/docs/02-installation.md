# Installation Guide

Complete installation instructions for Iltero CLI across all platforms.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
- [Platform-Specific Instructions](#platform-specific-instructions)
- [Installing Scanners](#installing-scanners)
- [Verify Installation](#verify-installation)
- [Upgrading](#upgrading)
- [Uninstalling](#uninstalling)

## Prerequisites

Before installing Iltero CLI, ensure you have:

- **Python 3.11 or higher** - Check with `python --version` or `python3 --version`
- **pip** - Python package installer (usually included with Python)
- **Git** (optional) - For installing from source
- **Iltero account** - Sign up at [iltero.io](https://iltero.io)

### Checking Python Version

```bash
# Check Python version
python --version
# or
python3 --version

# Should output: Python 3.11.x or higher
```

If you need to install or upgrade Python:
- **macOS**: Use [Homebrew](https://brew.sh/) - `brew install python@3.11`
- **Linux**: Use your package manager - `sudo apt install python3.11` (Ubuntu/Debian)
- **Windows**: Download from [python.org](https://www.python.org/downloads/)

## Installation Methods

### Option 1: Install from PyPI (Recommended)

The easiest way to install Iltero CLI is from PyPI:

```bash
pip install iltero-cli
```

Or if you need to use `pip3`:

```bash
pip3 install iltero-cli
```

**Troubleshooting:**
- If you get a "permission denied" error, use `pip install --user iltero-cli`
- If `pip` is not found, try `python -m pip install iltero-cli`

### Option 2: Install from Source

For development or to get the latest unreleased features:

```bash
# Clone the repository
git clone https://github.com/iltero/iltero-cli.git
cd iltero-cli

# Install in editable mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Option 3: Using a Virtual Environment (Recommended)

Virtual environments isolate dependencies and prevent conflicts:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Install Iltero CLI
pip install iltero-cli

# When done, deactivate
deactivate
```

### Option 4: Using pipx (Isolated Installation)

[pipx](https://pypa.github.io/pipx/) installs CLI tools in isolated environments:

```bash
# Install pipx (if not already installed)
python -m pip install --user pipx
python -m pipx ensurepath

# Install Iltero CLI
pipx install iltero-cli

# Upgrade later
pipx upgrade iltero-cli
```

## Platform-Specific Instructions

### macOS

```bash
# Option 1: Direct installation
pip3 install iltero-cli

# Option 2: Using Homebrew (when available)
# brew tap iltero/tap
# brew install iltero-cli

# Verify installation
iltero --version
```

**Common Issues:**
- If you get SSL certificate errors, upgrade your certificates: `pip install --upgrade certifi`
- If `iltero` command is not found, add `~/.local/bin` to your PATH

### Linux (Ubuntu/Debian)

```bash
# Ensure Python 3.11+ is installed
sudo apt update
sudo apt install python3.11 python3-pip

# Install Iltero CLI
pip3 install iltero-cli

# Add to PATH if needed
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify installation
iltero --version
```

### Linux (RHEL/CentOS/Fedora)

```bash
# Ensure Python 3.11+ is installed
sudo dnf install python3.11 python3-pip

# Install Iltero CLI
pip3 install iltero-cli

# Verify installation
iltero --version
```

### Windows

```powershell
# Using PowerShell

# Install Python from python.org if needed
# Then install Iltero CLI
pip install iltero-cli

# Verify installation
iltero --version
```

**Common Issues:**
- If `iltero` is not recognized, add Python Scripts directory to PATH:
  - Default location: `C:\Users\<username>\AppData\Local\Programs\Python\Python311\Scripts`
- Consider using Windows Terminal for better CLI experience

### Docker

Run Iltero CLI in a Docker container:

```bash
# Pull the image (when available)
docker pull iltero/cli:latest

# Run a command
docker run --rm -v $(pwd):/workspace \
  -e ILTERO_TOKEN=$ILTERO_TOKEN \
  iltero/cli:latest scan static --path /workspace

# Create an alias for convenience
alias iltero='docker run --rm -v $(pwd):/workspace -e ILTERO_TOKEN iltero/cli:latest'
```

## Installing Scanners

Iltero CLI can run local compliance scans using these scanners:

### Checkov (Infrastructure as Code Scanner)

```bash
# Install via pip
pip install checkov

# Verify installation
checkov --version
```

**Supported IaC formats:**
- Terraform
- CloudFormation
- Kubernetes
- Helm
- Dockerfile
- And more...

### OPA (Open Policy Agent)

**macOS:**
```bash
brew install opa
```

**Linux:**
```bash
# Download binary
curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64
chmod +x opa
sudo mv opa /usr/local/bin/

# Or use package manager
# Ubuntu/Debian
curl -L https://openpolicyagent.org/downloads/latest/opa_linux_amd64 -o opa
chmod +x opa
sudo mv opa /usr/local/bin/
```

**Windows:**
```powershell
# Download from https://www.openpolicyagent.org/downloads/
# Add to PATH
```

**Verify installation:**
```bash
opa version
```

### Cloud Custodian (Cloud Resource Scanner)

```bash
# Install via pip
pip install c7n c7n-org

# Verify installation
custodian version
```

**Supported cloud providers:**
- AWS
- Azure
- GCP

### Verify Scanner Installation

```bash
# Check all scanners
iltero scanner check

# Output:
# ✓ Checkov: v2.3.4 (installed)
# ✓ OPA: v0.45.0 (installed)
# ✗ Cloud Custodian: Not installed
```

## Verify Installation

After installation, verify everything is working:

```bash
# Check CLI version
iltero --version
# Output: iltero version 1.0.0

# View help
iltero --help

# Check which Python is being used
which iltero  # macOS/Linux
where iltero  # Windows

# Verify scanner detection
iltero scanner check
```

## Upgrading

### Upgrade from PyPI

```bash
# Upgrade to latest version
pip install --upgrade iltero-cli

# Upgrade to specific version
pip install --upgrade iltero-cli==1.2.0

# Using pipx
pipx upgrade iltero-cli
```

### Upgrade from Source

```bash
cd iltero-cli
git pull
pip install -e . --upgrade
```

## Uninstalling

### Remove Iltero CLI

```bash
# Using pip
pip uninstall iltero-cli

# Using pipx
pipx uninstall iltero-cli
```

### Clean Up Configuration

```bash
# Remove configuration directory
rm -rf ~/.iltero

# Remove from keyring (macOS)
security delete-generic-password -s "iltero-cli" -a "api-token"
```

### Remove Scanners

```bash
# Remove Checkov
pip uninstall checkov

# Remove OPA
sudo rm /usr/local/bin/opa  # macOS/Linux

# Remove Cloud Custodian
pip uninstall c7n c7n-org
```

## Troubleshooting Installation

### Command Not Found

If `iltero` command is not found after installation:

**macOS/Linux:**
```bash
# Find where pip installed it
pip show -f iltero-cli | grep Location

# Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**Windows:**
```powershell
# Find installation location
pip show iltero-cli

# Add to PATH via System Properties > Environment Variables
# Add: C:\Users\<username>\AppData\Local\Programs\Python\Python311\Scripts
```

### Permission Denied

```bash
# Install for current user only
pip install --user iltero-cli

# Or use virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate
pip install iltero-cli
```

### SSL Certificate Errors

```bash
# Upgrade certificates
pip install --upgrade certifi

# Or install with --trusted-host
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org iltero-cli
```

### Incompatible Python Version

```bash
# Check Python version
python --version

# If < 3.11, install newer Python
# macOS
brew install python@3.11

# Ubuntu/Debian
sudo apt install python3.11 python3.11-venv

# Then create venv with specific version
python3.11 -m venv .venv
source .venv/bin/activate
pip install iltero-cli
```

## Next Steps

After successful installation:

1. **Configure Authentication** - See [Quickstart Guide](quickstart.md#authentication)
2. **Run Your First Scan** - See [Quickstart Guide](quickstart.md#your-first-scan)
3. **Set Up CI/CD** - See [CI/CD Integration](ci-cd/README.md)
4. **Explore Commands** - See [Command Reference](commands/index.md)

## Getting Help

If you encounter installation issues:

1. Check the [Troubleshooting Guide](troubleshooting.md)
2. Search [GitHub Issues](https://github.com/iltero/iltero-cli/issues)
3. Create a [new issue](https://github.com/iltero/iltero-cli/issues/new) with:
   - Your OS and Python version
   - Installation method used
   - Full error message
   - Output of `pip list | grep iltero`

---

**Related Documentation:**
- [Quickstart Guide](quickstart.md)
- [Configuration Guide](configuration.md)
- [Troubleshooting Guide](troubleshooting.md)
