# macOS Junk Cleaner

[![CI](https://github.com/joaomartinscaetano/macos-junk-cleaner/actions/workflows/ci.yml/badge.svg)](https://github.com/joaomartinscaetano/macos-junk-cleaner/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/macos-junk-cleaner.svg)](https://pypi.org/project/macos-junk-cleaner/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Semantic Release](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg)](https://github.com/python-semantic-release/python-semantic-release)

A Python-based CLI utility to scan and remove macOS-specific junk files (e.g., `.DS_Store`, `._*`, `.Spotlight-V100`) from directories.

## Installation

### Using pip
```bash
pip install .
```

### Using uv
```bash
uv tool install .
```

## Usage

### Scan
To see what would be cleaned with a detailed summary:
```bash
mac-clean scan /path/to/dir
# or using uv
uv run mac-clean scan /path/to/dir
```

### Clean
The `clean` command is used for removal. For safety, it **defaults to dry-run mode**.

```bash
# Preview deletion (Dry-run)
mac-clean clean /path/to/dir

# Perform actual deletion
mac-clean clean /path/to/dir --force
```

## Development

### Setup (uv)
1. Clone the repository.
2. Sync the environment (creates venv and installs all dependencies and dev tools):
   ```bash
   uv sync
   ```
3. Install pre-commit hooks:
   ```bash
   uv run pre-commit install
   ```

### Linting and Formatting
This project uses [Ruff](https://github.com/astral-sh/ruff) for linting and formatting.

```bash
# Lint
ruff check .
# or using uv
uv run ruff check .

# Format
ruff format .
# or using uv
uv run ruff format .
```

### Testing
```bash
pytest
# or using uv
uv run pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

