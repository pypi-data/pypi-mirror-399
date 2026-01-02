# Packaging & Distribution

Guide for building and distributing the Iltero CLI.

## Overview

The Iltero CLI is distributed through multiple channels:

- **PyPI** - Python Package Index (`pip install iltero-cli`)
- **Source distributions** - Tarball and wheel packages
- **Future**: Homebrew, apt/yum repositories, standalone binaries

## Package Structure

```
iltero-cli/
├── iltero/                    # Main package
│   ├── __init__.py
│   ├── cli.py                # CLI entry point
│   ├── commands/             # Command modules
│   ├── core/                 # Core functionality
│   └── scanners/             # Scanner integrations
├── completions/              # Shell completions (included in package)
├── pyproject.toml           # Package metadata and dependencies
├── README.md                # Package description
└── LICENSE                  # Apache 2.0 license
```

## Building Packages

### Prerequisites

- Python 3.11+
- PDM (Python Development Master)
- Clean git working directory (recommended)

### Build Process

**1. Verify package configuration:**

```bash
# Check pyproject.toml for correct version, dependencies, etc.
cat pyproject.toml
```

**2. Build distribution packages:**

```bash
# Build both source distribution (.tar.gz) and wheel (.whl)
pdm build
```

This creates:
- `dist/iltero_cli-VERSION.tar.gz` - Source distribution
- `dist/iltero_cli-VERSION-py3-none-any.whl` - Universal wheel

**3. Verify build artifacts:**

```bash
ls -lh dist/
```

Expected output:
```
iltero_cli-0.1.0-py3-none-any.whl  (~1.3 MB)
iltero_cli-0.1.0.tar.gz            (~554 KB)
```

## Testing Package Installation

### Local Testing

**Test in clean virtual environment:**

```bash
# Create test environment
cd /tmp
python3 -m venv test_iltero
source test_iltero/bin/activate

# Install from local wheel
pip install /path/to/iltero-cli/dist/iltero_cli-VERSION-py3-none-any.whl

# Verify installation
iltero --version
iltero --help

# Test basic functionality
iltero auth status

# Clean up
deactivate
rm -rf test_iltero
```

**Test from source distribution:**

```bash
# Create test environment
python3 -m venv test_iltero_src
source test_iltero_src/bin/activate

# Install from tarball
pip install /path/to/iltero-cli/dist/iltero_cli-VERSION.tar.gz

# Verify
iltero --version

# Clean up
deactivate
rm -rf test_iltero_src
```

### Automated Testing

**Create test script:**

```bash
#!/bin/bash
set -e

VERSION="0.1.0"
WHEEL="dist/iltero_cli-${VERSION}-py3-none-any.whl"

# Create test environment
python3 -m venv /tmp/test_iltero
source /tmp/test_iltero/bin/activate

# Install package
pip install "$WHEEL"

# Run tests
iltero --version | grep "$VERSION"
iltero --help > /dev/null
iltero auth --help > /dev/null

# Verify entry point
which iltero

# Clean up
deactivate
rm -rf /tmp/test_iltero

echo "✅ Package installation test passed"
```

## Publishing to PyPI

### Prerequisites

- PyPI account (https://pypi.org/account/register/)
- API token from PyPI account settings
- PDM configured with token

### Configuration

**1. Configure PyPI credentials:**

```bash
# Set PyPI token
pdm config pypi.token "pypi-..."

# Or use environment variable
export PDM_PUBLISH_PASSWORD="pypi-..."
```

**2. Verify configuration:**

```bash
pdm config pypi.token
```

### Publishing Process

**1. Test on TestPyPI first (recommended):**

```bash
# Build package
pdm build

# Publish to TestPyPI
pdm publish --repository testpypi

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ iltero-cli
```

**2. Publish to production PyPI:**

```bash
# Build clean package
rm -rf dist/
pdm build

# Verify version is correct
grep version pyproject.toml

# Publish to PyPI
pdm publish

# Verify on PyPI
open https://pypi.org/project/iltero-cli/
```

**3. Test installation from PyPI:**

```bash
# Create clean environment
python3 -m venv /tmp/test_pypi
source /tmp/test_pypi/bin/activate

# Install from PyPI
pip install iltero-cli

# Verify
iltero --version

# Clean up
deactivate
rm -rf /tmp/test_pypi
```

## Version Management

### Version Bumping

**Update version in pyproject.toml:**

```toml
[project]
name = "iltero-cli"
version = "1.0.0"  # Update this
```

**Commit version change:**

```bash
git add pyproject.toml
git commit -m "Bump version to 1.0.0"
git tag v1.0.0
git push origin main --tags
```

### Semantic Versioning

Follow [SemVer](https://semver.org/):

- **MAJOR** (1.0.0 → 2.0.0) - Breaking changes
- **MINOR** (1.0.0 → 1.1.0) - New features, backwards compatible
- **PATCH** (1.0.0 → 1.0.1) - Bug fixes, backwards compatible

**Examples:**

```bash
# Patch release (bug fixes)
version = "1.0.1"

# Minor release (new features)
version = "1.1.0"

# Major release (breaking changes)
version = "2.0.0"
```

## Package Contents

### What's Included

The built package includes:

- **Source code**: All Python modules in `iltero/`
- **Completions**: Shell completion scripts in `completions/`
- **Metadata**: README, LICENSE, pyproject.toml
- **Dependencies**: Listed in `[project.dependencies]`

### What's Excluded

Build excludes development files:

- `tests/` - Test suite
- `.venv/` - Virtual environment
- `htmlcov/` - Coverage reports
- `*.pyc`, `__pycache__/` - Bytecode
- `.git/` - Git repository

**Exclusion configuration:**

PDM automatically excludes common patterns. To customize:

```toml
[tool.hatch.build.targets.wheel]
packages = ["iltero"]
exclude = [
    "tests/",
    "htmlcov/",
    "*.pyc",
]
```

## Distribution Channels

### Current: PyPI

**Installation:**
```bash
pip install iltero-cli
```

**Features:**
- ✅ Cross-platform (macOS, Linux, Windows)
- ✅ Automatic dependency resolution
- ✅ Version management
- ✅ Virtual environment support

### Future: Homebrew (macOS/Linux)

**Planned installation:**
```bash
brew install iltero-cli
```

**Homebrew formula template:**
```ruby
class IlteroCli < Formula
  desc "Unified CLI for Iltero platform"
  homepage "https://github.com/iltero/iltero-cli"
  url "https://files.pythonhosted.org/packages/.../iltero_cli-1.0.0.tar.gz"
  sha256 "..."
  license "Apache-2.0"

  depends_on "python@3.11"

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/iltero", "--version"
  end
end
```

### Future: Standalone Binaries

**Using PyInstaller or Nuitka:**

```bash
# Install packaging tool
pip install pyinstaller

# Create standalone binary
pyinstaller --onefile \
  --name iltero \
  --console \
  iltero/cli.py

# Binary created in dist/iltero
```

**Benefits:**
- No Python installation required
- Single executable file
- Platform-specific builds

**Platforms:**
- macOS (ARM64 and x86_64)
- Linux (x86_64)
- Windows (x86_64)

## Continuous Integration

### GitHub Actions Workflow

**Automated publishing on tag:**

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install PDM
        run: pip install pdm
      
      - name: Build package
        run: pdm build
      
      - name: Publish to PyPI
        env:
          PDM_PUBLISH_PASSWORD: ${{ secrets.PYPI_TOKEN }}
        run: pdm publish
```

## Troubleshooting

### Build Failures

**Issue:** `ERROR: hatchling not found`

**Solution:**
```bash
pdm install
pdm build
```

### Import Errors After Installation

**Issue:** `ModuleNotFoundError: No module named 'iltero'`

**Solution:**
```bash
# Verify package structure
tar -tzf dist/iltero_cli-*.tar.gz | grep iltero/

# Should show iltero/ directory structure
```

### Version Conflicts

**Issue:** `ERROR: version already exists on PyPI`

**Solution:**
```bash
# Bump version in pyproject.toml
version = "1.0.1"

# Rebuild and publish
rm -rf dist/
pdm build
pdm publish
```

### Missing Dependencies

**Issue:** Package installs but CLI doesn't work

**Solution:**
```bash
# Verify dependencies in pyproject.toml
# Check if all required packages are listed

# Test in clean environment
python3 -m venv test_env
source test_env/bin/activate
pip install dist/iltero_cli-*.whl
iltero --help
```

## Best Practices

### Pre-Release Checklist

- [ ] All tests passing (`pdm run pytest`)
- [ ] Version bumped in `pyproject.toml`
- [ ] CHANGELOG updated
- [ ] README accurate
- [ ] Documentation updated
- [ ] Clean build (`rm -rf dist/`)
- [ ] Git working directory clean
- [ ] Tag created (`git tag v1.0.0`)

### Release Workflow

1. **Prepare release**
   ```bash
   # Update version
   vim pyproject.toml
   
   # Update changelog
   vim CHANGELOG.md
   
   # Commit changes
   git add pyproject.toml CHANGELOG.md
   git commit -m "Prepare release v1.0.0"
   ```

2. **Build and test**
   ```bash
   # Clean build
   rm -rf dist/
   pdm build
   
   # Test installation
   pip install dist/iltero_cli-*.whl
   iltero --version
   ```

3. **Publish**
   ```bash
   # Tag release
   git tag v1.0.0
   git push origin main --tags
   
   # Publish to PyPI
   pdm publish
   ```

4. **Verify**
   ```bash
   # Check PyPI page
   open https://pypi.org/project/iltero-cli/
   
   # Test installation from PyPI
   pip install --upgrade iltero-cli
   ```

## See Also

- [Developer Guide](05-developer-guide.md) - Development setup and workflows
- [Configuration Guide](03-configuration.md) - CLI configuration
- [Quickstart Guide](01-quickstart.md) - Installation and usage
