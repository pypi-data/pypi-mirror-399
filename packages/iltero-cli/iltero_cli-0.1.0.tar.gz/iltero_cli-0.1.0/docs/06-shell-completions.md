# Shell Completions

Enable tab completion for the Iltero CLI in your shell.

## Overview

Shell completions provide:

- **Tab completion** for commands, subcommands, and options
- **Faster workflow** - Type less, accomplish more
- **Command discovery** - See available commands as you type
- **Parameter hints** - View options and flags on the fly

The Iltero CLI supports completions for:
- **Bash** 4.4+
- **Zsh** 5.0+
- **Fish** 3.0+

## Quick Installation

### Automatic Installation

The easiest way to install completions:

```bash
# Installs completion for your current shell
iltero --install-completion

# Restart your shell or source the config file
exec $SHELL
```

This automatically:
- Detects your shell (bash, zsh, or fish)
- Generates the completion script
- Adds it to your shell's configuration file
- Activates completions for future sessions

### Manual Installation

If you prefer manual installation or need custom setup:

#### Bash

**Option 1: User installation (recommended)**

```bash
# Generate completion script
iltero --show-completion bash > ~/.iltero-completion.bash

# Add to your ~/.bashrc
echo 'source ~/.iltero-completion.bash' >> ~/.bashrc

# Reload your shell
source ~/.bashrc
```

**Option 2: System-wide installation**

```bash
# Generate completion script (requires sudo)
sudo iltero --show-completion bash > /etc/bash_completion.d/iltero

# Reload completions
source /etc/bash_completion.d/iltero
```

#### Zsh

**Option 1: User installation (recommended)**

```bash
# Generate completion script
iltero --show-completion zsh > ~/.iltero-completion.zsh

# Add to your ~/.zshrc
echo 'source ~/.iltero-completion.zsh' >> ~/.zshrc

# Reload your shell
source ~/.zshrc
```

**Option 2: Using completion directory**

```bash
# Create completions directory if needed
mkdir -p ~/.zfunc

# Generate completion script
iltero --show-completion zsh > ~/.zfunc/_iltero

# Add to your ~/.zshrc (if not already present)
echo 'fpath=(~/.zfunc $fpath)' >> ~/.zshrc
echo 'autoload -Uz compinit && compinit' >> ~/.zshrc

# Reload your shell
source ~/.zshrc
```

#### Fish

```bash
# Generate completion script
iltero --show-completion fish > ~/.config/fish/completions/iltero.fish

# Completions are automatically loaded
# No need to edit config files or reload
```

## Pre-Generated Scripts

For offline installation or when the CLI isn't installed yet, use the pre-generated scripts in the `completions/` directory:

```bash
# Available in the repository
completions/
├── iltero-completion.bash
├── iltero-completion.zsh
└── iltero-completion.fish
```

### Using Pre-Generated Scripts

**Bash:**
```bash
cp completions/iltero-completion.bash ~/.iltero-completion.bash
echo 'source ~/.iltero-completion.bash' >> ~/.bashrc
source ~/.bashrc
```

**Zsh:**
```bash
cp completions/iltero-completion.zsh ~/.iltero-completion.zsh
echo 'source ~/.iltero-completion.zsh' >> ~/.zshrc
source ~/.zshrc
```

**Fish:**
```bash
cp completions/iltero-completion.fish ~/.config/fish/completions/iltero.fish
```

## Verifying Installation

Test that completions are working:

```bash
# Type this and press TAB (don't press Enter)
iltero <TAB>

# You should see available commands:
# auth  token  workspace  environment  stack  scan  ...
```

### Testing Subcommand Completion

```bash
# Type this and press TAB
iltero workspace <TAB>

# Should show workspace subcommands:
# list  create  get  update  delete  set-default
```

### Testing Option Completion

```bash
# Type this and press TAB
iltero scan run --<TAB>

# Should show available options:
# --stack  --scanner  --threshold  --format  --help
```

## Troubleshooting

### Completions Not Working

**Issue:** Tab completion doesn't show any suggestions

**Solutions:**

1. **Verify completion is loaded:**
   ```bash
   # Bash
   complete -p iltero
   
   # Zsh
   which _iltero_completion
   
   # Fish
   complete -c iltero
   ```

2. **Check shell version:**
   ```bash
   # Bash (need 4.4+)
   bash --version
   
   # Zsh (need 5.0+)
   zsh --version
   
   # Fish (need 3.0+)
   fish --version
   ```

3. **Reinstall completions:**
   ```bash
   iltero --install-completion
   exec $SHELL
   ```

### Completion Script Not Found

**Issue:** `source: no such file or directory`

**Solution:**
```bash
# Verify the file exists
ls -l ~/.iltero-completion.zsh  # or .bash

# Regenerate if missing
iltero --show-completion zsh > ~/.iltero-completion.zsh
```

### Completions Out of Date

**Issue:** New commands don't appear in completions

**Solution:**
```bash
# Regenerate completion script
iltero --show-completion zsh > ~/.iltero-completion.zsh

# Reload shell
source ~/.zshrc
```

## How It Works

The Iltero CLI uses [Typer](https://typer.tiangolo.com/)'s built-in completion system:

1. **Dynamic completion**: Completions are generated at runtime based on available commands
2. **Context-aware**: Suggests relevant options based on what you've typed
3. **Automatic updates**: Completions reflect CLI changes without manual updates

### Completion Process

When you press TAB:

1. Shell calls the completion function (`_iltero_completion`)
2. Completion script invokes `iltero` with special environment variables
3. CLI analyzes current command context
4. Returns list of valid completions
5. Shell displays suggestions

## Advanced Usage

### Custom Completion Installation Path

```bash
# Install to custom location
iltero --show-completion zsh > /path/to/custom/_iltero

# Update your shell config to source it
echo 'source /path/to/custom/_iltero' >> ~/.zshrc
```

### CI/CD Environments

For automated environments, use the pre-generated scripts:

```bash
# Copy from repository
cp completions/iltero-completion.bash /etc/bash_completion.d/iltero
```

### Multiple Shell Support

If you use multiple shells:

```bash
# Install for all shells
iltero --show-completion bash > ~/.iltero-completion.bash
iltero --show-completion zsh > ~/.iltero-completion.zsh
iltero --show-completion fish > ~/.config/fish/completions/iltero.fish

# Add to respective config files
echo 'source ~/.iltero-completion.bash' >> ~/.bashrc
echo 'source ~/.iltero-completion.zsh' >> ~/.zshrc
```

## See Also

- [Quickstart Guide](01-quickstart.md) - Get started with the CLI
- [Configuration Guide](03-configuration.md) - Configure the CLI
- [Command Reference](commands/index.md) - All available commands
