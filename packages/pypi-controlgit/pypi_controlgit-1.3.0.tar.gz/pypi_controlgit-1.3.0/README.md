# ControlGit

ControlGit is a lightweight Git account and repository settings management tool. It's a subset of SmartGit focused on controlling Git configuration without deployment capabilities.

## Features

- **Account Settings**: Manage global Git user configuration
- **Repository Settings**: Manage repository-specific Git configuration
- **Remote Management**: Add, remove, and update Git remotes
- **GitHub Authentication**: Store and manage GitHub credentials
- **GitHub CLI Integration**: Optional integration with GitHub CLI

## Installation

```bash
pip install pypi-controlgit
```

## Quick Start

### Account Management

```bash
# Show global Git configuration
controlgit account config

# Set user name
controlgit account name "Your Name"

# Set user email
controlgit account email "your.email@example.com"

# Set custom configuration
controlgit account set core.editor "vim"
```

### Repository Management

```bash
# Show repository configuration
controlgit repo config my-repo

# Set repository configuration
controlgit repo set my-repo core.ignorecase true

# List remotes
controlgit repo remotes my-repo

# Add remote
controlgit repo add-remote my-repo origin https://github.com/user/repo.git

# Remove remote
controlgit repo remove-remote my-repo origin

# Update remote URL
controlgit repo set-remote-url my-repo origin https://github.com/user/new-repo.git
```

### GitHub Authentication

```bash
# Set credentials manually
controlgit auth set username token --2fa 123456

# Use GitHub CLI for interactive login
controlgit auth set

# Check authentication status
controlgit auth status

# Clear credentials
controlgit auth clear
```

## Commands

### auth
- `auth set [username] [password]` - Set GitHub credentials
- `auth status` - Show authentication status
- `auth clear` - Clear stored credentials

### account
- `account config` - Show global Git configuration
- `account set <key> <value>` - Set global Git configuration
- `account name <name>` - Set global user name
- `account email <email>` - Set global user email

### repo
- `repo config <name>` - Show repository configuration
- `repo set <name> <key> <value>` - Set repository configuration
- `repo remotes <name>` - List repository remotes
- `repo add-remote <name> <remote-name> <url>` - Add remote
- `repo remove-remote <name> <remote-name>` - Remove remote
- `repo set-remote-url <name> <remote-name> <url>` - Update remote URL

## Options

- `--path <path>` - Working directory (default: current directory)
- `--github-user <username>` - GitHub username (default: abucodingai)

## Requirements

- Python 3.8+
- Git 2.0+
- GitHub CLI (gh) 2.0+ (optional, for interactive login)

## License

MIT License

## Author

Abu Shariff (abu.shariffaiml@gmail.com)
