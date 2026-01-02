# Command Reference

Complete reference for all Iltero CLI commands.

## Command Groups

- **[Authentication Commands](01-auth.md)** - Manage authentication and API tokens
- **[Token Commands](02-token.md)** - Create and manage API tokens
- **[Workspace Commands](03-workspace.md)** - Manage workspaces
- **[Environment Commands](04-environment.md)** - Manage environments within workspaces
- **[Stack Commands](05-stack.md)** - Manage infrastructure stacks
- **[Scan Commands](06-scan.md)** - Run compliance scans
- **[Scanner Commands](07-scanner.md)** - Manage and configure scanners
- **[Compliance Commands](08-compliance.md)** - Check compliance status and violations
- **[Context Commands](09-context.md)** - Manage CLI context and defaults
- **[Repository Commands](10-repository.md)** - Manage Git repository integrations
- **[Bundles Commands](11-bundles.md)** - Manage compliance bundles and policies
- **[Registry Commands](12-registry.md)** - Manage module and template registry
- **[Organization Commands](13-org.md)** - Manage organizations
- **[User Commands](14-user.md)** - Manage users and permissions

## Global Options

These options are available for all commands:

```bash
--output FORMAT     # Output format: table, json, yaml (default: table)
--debug             # Enable debug logging
--no-color          # Disable colored output
--help              # Show help message
--version           # Show CLI version
```

## Exit Codes

The CLI uses standard exit codes:

- `0` - Success
- `1` - General error
- `2` - Authentication error
- `3` - Validation error
- `4` - Scan found violations above threshold
- `5` - Network/API error

## Output Formats

All commands support multiple output formats:

### Table (Default)

Human-readable formatted table:
```bash
iltero workspace list
```

### JSON

Machine-readable JSON:
```bash
iltero workspace list --output json
```

### YAML

YAML format:
```bash
iltero workspace list --output yaml
```

## Command Structure

All Iltero CLI commands follow this pattern:

```
iltero [COMMAND_GROUP] [SUBCOMMAND] [OPTIONS] [ARGUMENTS]
```

For example:
```bash
iltero workspace list --output json
│      │         │     └─ Option
│      │         └─ Subcommand
│      └─ Command group
└─ CLI name
```

## Getting Help

```bash
# General help
iltero --help

# Help for a command group
iltero workspace --help

# Help for a specific command
iltero workspace create --help
```

## Common Workflows

For workflow examples and complete guides, see:

- [Getting Started Guide](../quickstart.md)
- [CI/CD Integration](../ci-cd/README.md)
- [Configuration Guide](../configuration.md)

---

**Browse by command group above or search for specific commands.**
