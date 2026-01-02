# dbt-to-cypher

Extract dependency graphs from dbt projects (including model and column dependencies) and convert them to Cypher queries for graph database visualization and analysis.

## Features

- **Model-level dependencies**: Extract relationships between dbt models
- **Column-level lineage**: Track data flow at the column level
- **Cypher generation**: Convert dependency graphs to Neo4j Cypher queries
- **CLI tool**: Easy command-line interface for quick conversions
- **Library API**: Programmatic access for integration into your workflows

## Installation

Using `uv` (recommended):

```bash
uv pip install dbt-to-cypher
```

Using `pip`:

```bash
pip install dbt-to-cypher
```

## Quick Start

### Command Line

```bash
# Basic usage
dbt-to-cypher /path/to/dbt/project

# Save output to file
dbt-to-cypher /path/to/dbt/project -o output.cypher

```

### Python API

The `dbt_to_cypher` module provides a high-level API for programmatic access:

```python
from dbt_to_cypher import extract_dbt_project

cypher_script = extract_dbt_project(
    project_path="/path/to/dbt/project",
    output_path="output.cypher",  # Optional
)
print(cypher_script)
```

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for development setup instructions.

### Quick Development Setup

```bash
# Install uv
pip install uv

# Create virtual environment and install dependencies
uv venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

## Project Structure

```
dbt-to-cypher/
├── src/
│   └── dbt_to_cypher/
│       ├── __init__.py           # Package initialization and exports
│       ├── dbt_to_cypher.py      # Core API for dbt-to-cypher conversion
│       ├── extractor.py          # dbt dependency extraction
│       ├── graph.py              # Dependency graph management
│       ├── cypher.py             # Cypher query generation
│       └── cli.py                # Command-line interface
├── tests/                        # Test suite
├── pyproject.toml               # PEP 621 project metadata
├── .pre-commit-config.yaml      # Pre-commit hooks configuration
└── README.md
```

### Core Modules

- **dbt_to_cypher.py**: Main API module providing high-level functions for the conversion pipeline
- **extractor.py**: Parses dbt `manifest.json` and `catalog.json` to extract model and column-level dependencies
- **graph.py**: Builds and manages a NetworkX-based dependency graph with models and columns as nodes
- **cypher.py**: Generates Neo4j Cypher CREATE statements from the dependency graph

## Requirements

- Python 3.9+
- dbt project with generated `manifest.json` and `catalog.json` (run `dbt compile` and `dbt docs generate` first)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Release a new version in PyPi

Update version name in `pyproject.toml`, and create a new release in Github to release a new version.
The new release will need to be in main branch only.
It will automatically publish to PyPi.

## Roadmap

- [ ] Parse dbt `manifest.json` for model dependencies
- [ ] Extract column-level lineage from SQL queries
- [ ] Support for dbt sources and seeds
- [ ] Export to additional graph formats (GraphML, DOT)
- [ ] Interactive visualization tools
- [ ] Support for dbt metrics and exposures

## Author

laphoang

## Acknowledgments

Built with modern Python packaging standards (PEP 621) and best practices.
