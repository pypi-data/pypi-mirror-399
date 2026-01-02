# Iltero CLI Documentation

Welcome to the Iltero CLI documentation! This guide will help you get started with infrastructure compliance scanning and management.

## 📚 Documentation Index

### Getting Started

- **[Quickstart Guide](01-quickstart.md)** - Get up and running in 5 minutes
- **[Installation Guide](02-installation.md)** - Detailed installation instructions for all platforms
- **[Configuration Guide](03-configuration.md)** - Configure the CLI with environment variables and config files

### Command Reference

- **[Commands Overview](commands/index.md)** - Overview of all available commands
- **[Authentication Commands](commands/01-auth.md)** - Manage authentication and verify connectivity
- **[Token Commands](commands/02-token.md)** - Create and manage API tokens
- **[Workspace Commands](commands/03-workspace.md)** - Manage workspaces
- **[Environment Commands](commands/04-environment.md)** - Manage environments within workspaces
- **[Stack Commands](commands/05-stack.md)** - Manage infrastructure stacks
- **[Scan Commands](commands/06-scan.md)** - Run compliance scans
- **[Scanner Commands](commands/07-scanner.md)** - Manage and configure scanners
- **[Compliance Commands](commands/08-compliance.md)** - Check compliance status and history
- **[Context Commands](commands/09-context.md)** - Manage CLI context and settings
- **[Repository Commands](commands/10-repository.md)** - Manage source repositories
- **[Bundles Commands](commands/11-bundles.md)** - Manage policy bundles
- **[Registry Commands](commands/12-registry.md)** - Manage policy registry and templates
- **[Organization Commands](commands/13-org.md)** - Manage organization settings
- **[User Commands](commands/14-user.md)** - Manage users and permissions

### CI/CD Integration

- **[CI/CD Overview](ci-cd/README.md)** - General guidance for CI/CD integration
- **[GitHub Actions](ci-cd/01-github-actions.md)** - Complete GitHub Actions integration
- **[GitLab CI](ci-cd/02-gitlab-ci.md)** - Complete GitLab CI/CD integration
- **[Jenkins](ci-cd/03-jenkins.md)** - Complete Jenkins pipeline integration
- **[Azure DevOps](ci-cd/04-azure-devops.md)** - Complete Azure Pipelines integration
- **[CircleCI](ci-cd/05-circleci.md)** - Complete CircleCI integration
- **[Bitbucket Pipelines](ci-cd/06-bitbucket-pipelines.md)** - Complete Bitbucket integration

### Additional Resources

- **[Troubleshooting Guide](04-troubleshooting.md)** - Common issues and solutions
- **[Developer Guide](05-developer-guide.md)** - Contributing and development setup
- **[Shell Completions](06-shell-completions.md)** - Enable tab completion for bash, zsh, and fish
- **[Packaging & Distribution](07-packaging.md)** - Building and publishing packages
- **[Example Configurations](examples/)** - Sample configuration files for various scenarios

## 🚀 Quick Links

### Most Common Tasks

1. **First Time Setup**
   ```bash
   # Install the CLI
   pip install iltero-cli
   
   # Authenticate
   iltero auth set-token
   
   # Verify setup
   iltero auth status
   ```

2. **Run a Compliance Scan**
   ```bash
   # Scan infrastructure code
   iltero scan static --path ./terraform
   
   # View results
   iltero compliance list
   ```

3. **Set Up CI/CD**
   - Create a [pipeline token](commands/token.md#create-pipeline-token)
   - Add token to CI/CD secrets
   - Follow platform-specific guide: [GitHub Actions](ci-cd/github-actions.md), [GitLab](ci-cd/gitlab-ci.md), etc.

4. **Manage Workspaces**
   ```bash
   # List workspaces
   iltero workspace list
   
   # Create workspace
   iltero workspace create --name "production"
   
   # Set active workspace
   iltero context set-workspace production
   ```

## 🆘 Getting Help

- **CLI Help**: Run `iltero --help` or `iltero <command> --help`
- **Troubleshooting**: See [troubleshooting.md](troubleshooting.md)
- **Issues**: Report bugs on [GitHub Issues](https://github.com/iltero/iltero-cli/issues)
- **Documentation**: Visit [docs.iltero.io](https://docs.iltero.io)
- **Support**: Contact support@iltero.io

## 📖 Document Conventions

Throughout this documentation:

- **Code blocks** show example commands you can run
- `--flags` and `arguments` are explained with each command
- **Output examples** show what to expect when running commands
- **Tips** 💡 provide best practices and shortcuts
- **Warnings** ⚠️ highlight important considerations

## 🔄 Version Information

This documentation is for Iltero CLI v1.0.0 and later.

To check your installed version:
```bash
iltero --version
```

To upgrade to the latest version:
```bash
pip install --upgrade iltero-cli
```

---

**Next Steps:**
- New to Iltero? Start with the [Quickstart Guide](01-quickstart.md)
- Setting up CI/CD? Jump to [CI/CD Integration](ci-cd/README.md)
- Looking for a specific command? Check the [Commands Overview](commands/index.md)
