# shiba-dev-tools

[![PyPI version](https://badge.fury.io/py/shiba-dev-tools.svg)](https://pypi.org/project/shiba-dev-tools/)
[![Python Versions](https://img.shields.io/pypi/pyversions/shiba-dev-tools.svg)](https://pypi.org/project/shiba-dev-tools/)
[![License](https://img.shields.io/github/license/leeaaron629/shiba-dev-tools.svg)](https://github.com/leeaaron629/shiba-dev-tools/blob/main/LICENSE)
[![CI Status](https://github.com/leeaaron629/shiba-dev-tools/workflows/CI/badge.svg)](https://github.com/leeaaron629/shiba-dev-tools/actions)

Developer tools in a CLI.

## Features

- **Configuration Management**: JSON-based config system with atomic writes, file locking, and global storage
- **GitHub Integration**: Manage pull requests and comments from the command line
- **Notebook Management**: Organize and manage development notes with category-based organization
- **Cross-Platform**: Works on Windows, macOS, and Linux with platform-aware directory handling
- **Type-Safe**: Fully typed with pyright for better IDE support
- **Global Data Storage**: Configs and notebooks stored globally (`~/.sdt/`) for multi-project use

## Installation

### From PyPI (Recommended)

```bash
pip install shiba-dev-tools
```

### From Source (Development)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/leeaaron629/shiba-dev-tools.git
cd shiba-dev-tools
make install
```

## Usage

After installation, the `sdt` command will be available. All data is stored globally in:
- macOS/Linux: `~/.sdt/`
- Windows: `%LOCALAPPDATA%/sdt/`
- Custom location: Set `SDT_HOME` environment variable

```bash
# View all commands
sdt --help

# Configuration management (stored in ~/.sdt/configs/)
sdt config create
sdt config set github.token ghp_xxxxx
sdt config set settings.timeout 60
sdt config get settings.timeout
sdt config edit  # Open config in $EDITOR

# GitHub integration
sdt github prs list --user octocat
sdt github prs comments 123

# Notebook management (stored in ~/.sdt/notebooks/)
sdt nb                              # List categories
sdt nb work                         # List notes in "work" category
sdt nb work standup --write "..."   # Write a note
sdt nb work standup                 # Read a note
sdt nb work standup --edit          # Edit in $EDITOR
sdt nb work --delete                # Archive category
```

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager (for development)

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, testing, and release process.

### Quick Start

```bash
# Install dependencies
make install

# Run tests with coverage
make test

# Run linting (ruff + pyright)
make lint

# Format code
make format

# Build the package
make build
```

### Code Quality

This project uses:
- **ruff** for linting and formatting
- **pyright** for type checking
- **pytest** for testing with coverage

```bash
# Run all checks
make lint

# Auto-format code
make format
```

## Project Structure

```
shiba-dev-tools/
├── .github/workflows/      # CI/CD workflows
├── dev_tools/              # Main source package
│   ├── main.py            # Root CLI app
│   ├── config.py          # Configuration management
│   ├── github.py          # GitHub integration
│   ├── notebook.py        # Notebook management
│   ├── paths.py           # Platform-aware path resolution
│   └── ...
├── dev_tools_tests/       # Test package
├── pyproject.toml         # Project configuration
├── Makefile               # Development commands
└── README.md              # This file
```

### Data Storage

All application data is stored in a global directory:

```
~/.sdt/                     # Global SDT directory
├── configs/               # Configuration files
│   └── config.json       # Default config
└── notebooks/             # Note storage
    ├── {category}/       # Note categories
    │   └── {slug}.txt    # Individual notes
    └── .archive/         # Archived categories
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history.
