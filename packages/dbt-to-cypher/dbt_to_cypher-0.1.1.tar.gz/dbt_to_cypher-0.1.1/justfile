# Justfile for dbt-to-cypher development tasks
# Install just: https://github.com/casey/just
# Run `just` to see available commands

# Default recipe (shows help)
default:
    @just --list

# Install development dependencies
install:
    uv pip install -e ".[dev]"
    pre-commit install

# Run all tests
test:
    pytest

# Run tests with coverage
test-cov:
    pytest --cov=src --cov-report=html --cov-report=term

# Format code with ruff
format:
    ruff format src tests

# Lint code with ruff
lint:
    ruff check src tests

# Lint and fix code with ruff
lint-fix:
    ruff check --fix src tests

# Type check with mypy
type-check:
    mypy src

# Run all pre-commit hooks
pre-commit:
    pre-commit run --all-files

# Check code quality (format + lint + type-check)
check: lint-fix format type-check

# Clean build artifacts
clean:
    rm -rf build/
    rm -rf dist/
    rm -rf *.egg-info
    rm -rf .pytest_cache
    rm -rf .coverage
    rm -rf htmlcov/
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

# Build the package
build:
    uv pip install build
    python -m build

# Run the CLI in development mode
run PROJECT_PATH *ARGS:
    python -m dbt_to_cypher.cli {{PROJECT_PATH}} {{ARGS}}

# Install pre-commit hooks
hooks:
    pre-commit install

# Update dependencies
update:
    uv pip install --upgrade -e ".[dev]"
    pre-commit autoupdate

# Create a new release (bump version and tag)
release VERSION:
    @echo "Creating release {{VERSION}}"
    # Update version in pyproject.toml and __init__.py
    @echo "Don't forget to:"
    @echo "1. Update version in pyproject.toml"
    @echo "2. Update version in src/dbt_to_cypher/__init__.py"
    @echo "3. git commit -am 'Release {{VERSION}}'"
    @echo "4. git tag v{{VERSION}}"
    @echo "5. git push && git push --tags"
