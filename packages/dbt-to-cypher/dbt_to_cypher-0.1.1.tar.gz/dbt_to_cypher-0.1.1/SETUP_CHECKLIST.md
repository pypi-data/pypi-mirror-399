# Project Setup Checklist

This checklist helps ensure your dbt-to-cypher development environment is properly configured.

## ✅ Initial Setup

- [ ] Clone the repository
- [ ] Python 3.8+ installed
- [ ] `uv` package manager installed (`pip install uv`)

## ✅ Environment Setup

### Option 1: Automated Setup (Recommended)

```bash
python setup_dev.py
```

### Option 2: Manual Setup

- [ ] Create virtual environment: `uv venv`
- [ ] Activate virtual environment:
  - Windows: `.venv\Scripts\activate`
  - Linux/Mac: `source .venv/bin/activate`
- [ ] Install dependencies: `uv pip install -e ".[dev]"`
- [ ] Install pre-commit hooks: `pre-commit install`

## ✅ Verify Installation

Run these commands to verify everything is working:

```bash
# Check Python version
python --version

# Check installed packages
uv pip list

# Run tests
pytest

# Check code formatting
ruff format --check src tests

# Lint code
ruff check src tests

# Type check
mypy src

# Run all pre-commit hooks
pre-commit run --all-files
```

## ✅ Configuration Files

Verify these files exist:

- [ ] `pyproject.toml` - Project metadata (PEP 621)
- [ ] `.pre-commit-config.yaml` - Pre-commit hooks (ruff, mypy)
- [ ] `.gitignore` - Git ignore patterns
- [ ] `LICENSE` - MIT License
- [ ] `README.md` - Project documentation
- [ ] `DEVELOPMENT.md` - Development guide

## ✅ Source Code

Verify package structure:

- [ ] `src/dbt_to_cypher/__init__.py` - Package initialization
- [ ] `src/dbt_to_cypher/extractor.py` - Dependency extraction
- [ ] `src/dbt_to_cypher/graph.py` - Graph management
- [ ] `src/dbt_to_cypher/cypher.py` - Cypher generation
- [ ] `src/dbt_to_cypher/cli.py` - Command-line interface

## ✅ Tests

Verify test structure:

- [ ] `tests/__init__.py` - Test package marker
- [ ] `tests/conftest.py` - Test configuration
- [ ] `tests/test_extractor.py` - Extractor tests
- [ ] `tests/test_graph.py` - Graph tests
- [ ] `tests/test_cypher.py` - Cypher generator tests

## ✅ Git Configuration

- [ ] Initialize git repository: `git init` (if not already done)
- [ ] Set up remote: `git remote add origin <url>`
- [ ] Create initial commit:
  ```bash
  git add .
  git commit -m "Initial project structure"
  git push -u origin main
  ```

## ✅ GitHub Configuration (Optional)

- [ ] Set up GitHub repository
- [ ] Enable GitHub Actions (CI workflow in `.github/workflows/ci.yml`)
- [ ] Configure branch protection rules
- [ ] Set up Codecov (optional)

## ✅ Development Workflow

Your typical development workflow should be:

1. Create feature branch: `git checkout -b feature/my-feature`
2. Write code
3. Run tests: `pytest`
4. Format code: `ruff format src tests`
5. Lint and fix: `ruff check --fix src tests`
6. Type check: `mypy src`
7. Commit changes (pre-commit hooks run automatically)
8. Push and create pull request

## ✅ Useful Commands

If you have `just` installed (optional):

```bash
just install      # Install dependencies
just test         # Run tests
just test-cov     # Run tests with coverage
just format       # Format code
just lint         # Lint code
just lint-fix     # Lint and fix code
just type-check   # Type check
just check        # Format + lint + type-check
just clean        # Clean build artifacts
```

## ✅ Next Steps

- [ ] Update `pyproject.toml` with your name and email
- [ ] Implement the TODOs in the source code
- [ ] Write additional tests
- [ ] Update documentation
- [ ] Create your first feature!

## 🎉 You're Ready!

If you've completed this checklist, your development environment is ready. Happy coding!
