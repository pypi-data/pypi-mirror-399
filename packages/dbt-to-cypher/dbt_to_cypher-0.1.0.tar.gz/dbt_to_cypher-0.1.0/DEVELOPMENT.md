# Development Setup

## Installation with uv

```bash
# Install uv if you haven't already
pip install uv

# Create a virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
uv pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

## Development Commands

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Format code
ruff format src tests

# Lint and fix code
ruff check --fix src tests

# Type check
mypy src

# Run pre-commit on all files
pre-commit run --all-files
```

## Building and Publishing

```bash
# Build the package
uv pip install build
python -m build

# Upload to PyPI (requires twine)
uv pip install twine
twine upload dist/*
```
