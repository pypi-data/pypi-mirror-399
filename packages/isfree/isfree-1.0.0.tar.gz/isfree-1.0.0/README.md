# isfree
[![Tests](https://github.com/rocktimsaikia/is-free/actions/workflows/test-package.yml/badge.svg)](https://github.com/rocktimsaikia/is-free/actions/workflows/test-package.yml)

Check if a domain is available using DNS.

## Installation

```bash
pip install isfree
```

## Usage

```bash
isfree example.com
```

Output:

```
✓ example.com is available
✗ google.com is taken
⚠ Invalid TLD: .invalidtld
```

Exit codes: `0` (available), `1` (taken), `2` (error)

## Development

```bash
# Clone and setup
git clone https://github.com/rocktimsaikia/is-free.git
cd is-free

# Install uv if not already installed
pip install uv

# Install package with dev dependencies
uv pip install -e ".[dev]"

# Setup pre-commit hooks
pre-commit install

# Run tests
python -m unittest
```
