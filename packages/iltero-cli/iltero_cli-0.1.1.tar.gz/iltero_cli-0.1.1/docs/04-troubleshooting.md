# Troubleshooting Guide

Common issues and solutions for the Iltero CLI.

## Table of Contents

- [Authentication Issues](#authentication-issues)
- [Connection Issues](#connection-issues)
- [Scanner Issues](#scanner-issues)
- [Installation Issues](#installation-issues)
- [Command Issues](#command-issues)
- [Performance Issues](#performance-issues)
- [Output Issues](#output-issues)
- [Platform-Specific Issues](#platform-specific-issues)
- [Getting Help](#getting-help)

## Authentication Issues

### Token Not Found

**Symptom:**
```
Error: No authentication token found
```

**Solution:**

1. Check if token is set:
   ```bash
   iltero auth show-token
   ```

2. Set token if missing:
   ```bash
   # Interactive mode
   iltero auth set-token

   # Or environment variable
   export ILTERO_TOKEN=itk_u_your_token_here
   ```

3. Verify token is valid:
   ```bash
   iltero auth status
   ```

### Invalid Token

**Symptom:**
```
Error: Invalid or expired authentication token (401 Unauthorized)
```

**Solutions:**

1. **Token expired** - Generate a new token:
   ```bash
   # Create new token in Iltero web UI
   # Then update CLI
   iltero auth set-token
   ```

2. **Wrong token format** - Verify token prefix:
   ```bash
   # Personal tokens start with: itk_u_
   # Pipeline tokens start with: itk_p_
   # Service tokens start with: itk_s_
   ```

3. **Token revoked** - Create a new token from the web UI

### Keyring Access Denied

**Symptom (macOS):**
```
Error: Could not access keychain
```

**Solution:**
```bash
# Allow Terminal/iTerm2 to access Keychain
# System Preferences > Security & Privacy > Privacy > Keychain

# Or use environment variable instead
export ILTERO_TOKEN=itk_u_your_token_here
```

**Symptom (Linux):**
```
Error: No keyring backend available
```

**Solution:**
```bash
# Install keyring backend
sudo apt-get install gnome-keyring  # Ubuntu/Debian
# or
sudo yum install gnome-keyring      # RHEL/CentOS

# Or use environment variable
export ILTERO_TOKEN=itk_u_your_token_here
```

### Wrong User/Organization

**Symptom:**
```
Error: Workspace not found
```

**Solution:**

1. Check authenticated user:
   ```bash
   iltero auth whoami
   ```

2. Verify you're in the correct organization:
   ```bash
   iltero org list
   ```

3. Set correct default organization:
   ```bash
   iltero context set org correct-org-name
   ```

## Connection Issues

### Cannot Connect to Backend

**Symptom:**
```
Error: Could not connect to API (Connection refused)
```

**Solutions:**

1. **Check API URL:**
   ```bash
   iltero auth status
   # Verify "API URL" is correct
   ```

2. **Test connectivity:**
   ```bash
   curl https://api.iltero.io/health
   # Should return: {"status": "healthy"}
   ```

3. **Check firewall/proxy:**
   ```bash
   # Set proxy if needed
   export HTTPS_PROXY=http://proxy.company.com:8080
   ```

4. **Verify SSL certificates:**
   ```bash
   # Temporary workaround (not recommended for production)
   export ILTERO_VERIFY_SSL=false
   ```

### Timeout Errors

**Symptom:**
```
Error: Request timeout after 30 seconds
```

**Solutions:**

1. **Increase timeout:**
   ```bash
   export ILTERO_REQUEST_TIMEOUT=60
   ```

2. **Check network speed:**
   ```bash
   ping api.iltero.io
   ```

3. **Try smaller requests:**
   ```bash
   # Instead of listing all
   iltero workspace list --limit 10
   ```

### SSL Certificate Errors

**Symptom:**
```
Error: SSL certificate verification failed
```

**Solutions:**

1. **Update certificates:**
   ```bash
   # macOS
   brew update && brew upgrade ca-certificates

   # Ubuntu/Debian
   sudo apt-get update && sudo apt-get install ca-certificates

   # RHEL/CentOS
   sudo yum update ca-certificates
   ```

2. **Check system time:**
   ```bash
   date
   # Ensure system clock is correct
   ```

3. **For self-hosted backends with self-signed certs:**
   ```bash
   export ILTERO_VERIFY_SSL=false
   # Or add cert to system trust store
   ```

## Scanner Issues

### Scanner Not Found

**Symptom:**
```
Error: Scanner 'checkov' not found in PATH
```

**Solutions:**

1. **Install missing scanner:**
   ```bash
   # Checkov
   pip install checkov

   # OPA
   brew install opa  # macOS
   # or download from: https://www.openpolicyagent.org/
   ```

2. **Verify installation:**
   ```bash
   iltero scanner check
   ```

3. **Specify custom path:**
   ```bash
   export ILTERO_CHECKOV_PATH=/custom/path/to/checkov
   export ILTERO_OPA_PATH=/custom/path/to/opa
   ```

### Scanner Timeout

**Symptom:**
```
Error: Scanner execution timeout after 300 seconds
```

**Solutions:**

1. **Increase timeout:**
   ```bash
   export ILTERO_SCAN_TIMEOUT=600  # 10 minutes
   ```

2. **Scan smaller directories:**
   ```bash
   # Instead of entire repo
   iltero scan static --path ./terraform/modules/vpc
   ```

3. **Exclude large files:**
   ```bash
   # Create .ilteroignore file
   cat > .ilteroignore << EOF
   *.tfstate
   *.tfstate.backup
   .terraform/
   node_modules/
   EOF
   ```

### Scanner Version Incompatibility

**Symptom:**
```
Error: Unsupported checkov version 1.x.x
```

**Solution:**
```bash
# Update scanner
pip install --upgrade checkov

# Verify version
checkov --version
iltero scanner check
```

### Permission Denied

**Symptom:**
```
Error: Permission denied: /path/to/directory
```

**Solutions:**

1. **Check directory permissions:**
   ```bash
   ls -la /path/to/directory
   ```

2. **Run with appropriate permissions:**
   ```bash
   # Change ownership
   sudo chown -R $(whoami) /path/to/directory

   # Or adjust permissions
   chmod 755 /path/to/directory
   ```

## Installation Issues

### Python Version Error

**Symptom:**
```
Error: Iltero CLI requires Python 3.11+
```

**Solutions:**

1. **Check Python version:**
   ```bash
   python --version
   # or
   python3 --version
   ```

2. **Install Python 3.11+:**
   ```bash
   # macOS
   brew install python@3.11

   # Ubuntu
   sudo apt-get install python3.11

   # Windows
   # Download from python.org
   ```

3. **Use correct Python:**
   ```bash
   python3.11 -m pip install iltero-cli
   ```

### Pip Installation Fails

**Symptom:**
```
Error: Could not find a version that satisfies the requirement iltero-cli
```

**Solutions:**

1. **Update pip:**
   ```bash
   python -m pip install --upgrade pip
   ```

2. **Install from source:**
   ```bash
   git clone https://github.com/iltero/iltero-cli.git
   cd iltero-cli
   pip install -e .
   ```

3. **Check Python version compatibility:**
   ```bash
   python --version  # Must be 3.11+
   ```

### Dependencies Conflict

**Symptom:**
```
Error: Cannot install iltero-cli due to dependency conflicts
```

**Solution:**
```bash
# Use virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install iltero-cli
```

### Command Not Found After Installation

**Symptom:**
```bash
iltero --version
# Command not found: iltero
```

**Solutions:**

1. **Check if installed:**
   ```bash
   pip show iltero-cli
   ```

2. **Add to PATH:**
   ```bash
   # Find installation path
   python -m site --user-base

   # Add to PATH in ~/.bashrc or ~/.zshrc
   export PATH="$HOME/.local/bin:$PATH"

   # Reload shell
   source ~/.bashrc
   ```

3. **Use full path:**
   ```bash
   python -m iltero --version
   ```

## Command Issues

### Command Not Recognized

**Symptom:**
```
Error: No such command 'workspaces'
```

**Solution:**
```bash
# Use correct command (singular form)
iltero workspace list  # Not 'workspaces'

# Check available commands
iltero --help
```

### Missing Required Arguments

**Symptom:**
```
Error: Missing required argument 'name'
```

**Solution:**
```bash
# Check command help
iltero workspace create --help

# Provide required arguments
iltero workspace create --name my-workspace
```

### Invalid JSON/YAML Output

**Symptom:**
```json
{
  "error": "Internal Server Error"
}
```

**Solutions:**

1. **Enable debug mode:**
   ```bash
   iltero --debug workspace list --output json
   ```

2. **Check API response:**
   ```bash
   iltero --debug auth status
   # Look for API response in output
   ```

3. **Try table output:**
   ```bash
   iltero workspace list --output table
   ```

## Performance Issues

### Slow Command Execution

**Solutions:**

1. **Enable caching:**
   ```yaml
   # ~/.iltero/config.yaml
   cache_enabled: true
   cache_ttl: 3600
   ```

2. **Use filters:**
   ```bash
   # Instead of listing everything
   iltero workspace list --limit 10
   iltero stack list --workspace specific-workspace
   ```

3. **Parallel execution:**
   ```yaml
   # ~/.iltero/config.yaml
   parallel_scans: true
   max_workers: 4
   ```

### Large Output Causes Issues

**Solutions:**

1. **Limit results:**
   ```bash
   iltero workspace list --limit 50
   ```

2. **Use pagination:**
   ```bash
   iltero workspace list --page 1 --page-size 25
   ```

3. **Filter early:**
   ```bash
   iltero compliance violations list --severity critical
   ```

## Output Issues

### Garbled Characters

**Symptom:**
```
[?25h[?25l��� Workspace
```

**Solutions:**

1. **Disable colors:**
   ```bash
   export ILTERO_NO_COLOR=true
   ```

2. **Set correct encoding:**
   ```bash
   export LC_ALL=en_US.UTF-8
   export LANG=en_US.UTF-8
   ```

### Table Too Wide

**Solution:**
```yaml
# ~/.iltero/config.yaml
max_column_width: 50
truncate_long_text: true
```

### Missing Colors

**Solution:**
```bash
# Ensure colors are enabled
unset ILTERO_NO_COLOR

# Check terminal color support
echo $TERM
# Should show: xterm-256color or similar
```

## Platform-Specific Issues

### macOS

#### Keychain Access Prompt

**Issue:** macOS asks for keychain password repeatedly

**Solution:**
```bash
# Allow "always allow" in keychain prompt
# Or use environment variable
export ILTERO_TOKEN=itk_u_your_token_here
```

#### Gatekeeper Blocking Scanner

**Issue:** "checkov cannot be opened because the developer cannot be verified"

**Solution:**
```bash
# Allow scanner in System Preferences
# Or install via Homebrew/pip
pip install checkov
```

### Windows

#### PowerShell Execution Policy

**Issue:**
```
iltero : File cannot be loaded because running scripts is disabled
```

**Solution:**
```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Path Issues

**Issue:** Command not found after installation

**Solution:**
```cmd
# Add Python Scripts to PATH
# Python installation directory\Scripts
set PATH=%PATH%;C:\Users\YourName\AppData\Local\Programs\Python\Python311\Scripts
```

### Linux

#### Keyring Backend Missing

**Issue:**
```
Error: No keyring backend available
```

**Solution:**
```bash
# Install keyring
sudo apt-get install gnome-keyring python3-keyring

# Or use environment variable
export ILTERO_TOKEN=itk_u_your_token_here
```

#### Permission Denied on Scanner

**Issue:**
```
Error: Permission denied: /usr/local/bin/checkov
```

**Solution:**
```bash
# Install in user space
pip install --user checkov

# Or fix permissions
chmod +x /usr/local/bin/checkov
```

## Debug Mode

Enable debug mode for detailed troubleshooting:

```bash
# Via flag
iltero --debug workspace list

# Via environment
export ILTERO_DEBUG=true
iltero workspace list

# With log file
export ILTERO_LOG_FILE=~/iltero-debug.log
iltero --debug workspace list
cat ~/iltero-debug.log
```

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `Authentication required` | No token set | Run `iltero auth set-token` |
| `Invalid token format` | Wrong token type | Check token starts with `itk_` |
| `Workspace not found` | Wrong context | Verify with `iltero workspace list` |
| `Scanner not found` | Scanner not installed | Run `pip install checkov` |
| `Connection refused` | Backend unreachable | Check `ILTERO_API_URL` |
| `Permission denied` | File permissions | Check directory permissions |
| `Timeout` | Request too slow | Increase `ILTERO_REQUEST_TIMEOUT` |

## Getting Help

### Check Version

```bash
iltero --version
```

### View Logs

```bash
# Enable logging
export ILTERO_LOG_FILE=~/.iltero/logs/cli.log
iltero workspace list

# View logs
tail -f ~/.iltero/logs/cli.log
```

### Generate Debug Report

```bash
# Collect diagnostic information
iltero debug report > debug-report.txt

# Share in issue report
```

### Community Support

- **Documentation**: https://docs.iltero.io
- **Issues**: https://github.com/iltero/iltero-cli/issues
- **Discussions**: https://github.com/iltero/iltero-cli/discussions
- **Community**: https://community.iltero.io
- **Support**: support@iltero.io

### Filing a Bug Report

Include the following information:

1. **CLI version**: `iltero --version`
2. **Python version**: `python --version`
3. **Operating system**: `uname -a` (Linux/macOS) or `ver` (Windows)
4. **Command executed**: Full command with `--debug` flag
5. **Error message**: Complete error output
6. **Expected behavior**: What should have happened
7. **Debug logs**: Relevant logs from `~/.iltero/logs/`

### Example Bug Report

```markdown
## Bug Description
`iltero workspace list` fails with authentication error

## Environment
- CLI version: 1.0.0
- Python version: 3.11.5
- OS: macOS 14.0 (ARM64)

## Steps to Reproduce
1. Install CLI: `pip install iltero-cli`
2. Set token: `iltero auth set-token`
3. Run: `iltero workspace list`

## Error Message
```
Error: Invalid or expired authentication token (401 Unauthorized)
```

## Expected Behavior
Should list all workspaces

## Debug Output
```
[Attach debug log]
```

## Additional Context
Token was just created and works in web UI
```

## See Also

- [Getting Started Guide](GETTING_STARTED.md)
- [Configuration Guide](CONFIGURATION.md)
- [Command Reference](COMMAND_REFERENCE.md)
