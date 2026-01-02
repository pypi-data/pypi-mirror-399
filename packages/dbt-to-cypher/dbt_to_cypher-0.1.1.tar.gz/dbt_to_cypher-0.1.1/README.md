# dbt-to-cypher

Extract dependency graphs from dbt projects (including model and column dependencies) and convert them to Cypher queries.

These queries can be used for graph database visualization and analysis in Neo4j or any other Cypher-compatible database.

## Purpose

This tool allows data engineers, analysts, and data scientists to gain insight into their data lineage and dependencies at both the model and column levels through a graph-based approach, improving data understanding and governance.

## Features

- **Model-level dependencies**: Extract relationships between dbt models.
- **Column-level lineage**: Track data flow at the column level
- **Cypher generation**: Convert dependency graphs to Neo4j Cypher queries
- **CLI tool**: Easy command-line interface for quick conversions
- **Library API**: Programmatic access for integration into your workflows

## Use Cases and Practical Applications

The `dbt-to-cypher` library is designed to provide actionable insights into data lineage and dependencies within dbt projects. It is particularly useful in large organizations or complex data pipelines where understanding relationships between models and columns is critical for data governance, debugging, and reporting. Some practical use cases include:

### 1. Data Lineage Visualization

Data engineers often struggle to understand how data flows through multiple layers of transformations in a dbt project. With `dbt-to-cypher`, you can generate Cypher scripts that create nodes and relationships in Neo4j, allowing you to visualize the full dependency graph. This visualization can help identify:

- Bottlenecks in your data pipeline
- Circular dependencies
- Unused or redundant models
- Models with high fan-in or fan-out dependencies

A clear visual representation of your data lineage can also help teams onboard new members more quickly and document complex pipelines effectively.

### 2. Impact Analysis

When making changes to dbt models, it is crucial to understand the potential impact on downstream models. By using `dbt-to-cypher` to generate a complete dependency graph, you can quickly query Neo4j to identify all downstream nodes that will be affected by a particular change. This capability is especially useful for:

- Regression testing
- Change management in production environments
- Risk assessment before deploying updates

Impact analysis reduces the risk of introducing errors and ensures that changes propagate safely through your pipeline.

### 3. Column-Level Lineage

In addition to model-level dependencies, `dbt-to-cypher` tracks column-level transformations. This allows you to:

- Understand how individual fields propagate through the pipeline
- Identify sensitive data flows for compliance purposes
- Trace the origin of a specific value or aggregated metric

Column-level lineage is critical for organizations dealing with regulated data or complex reporting structures, where understanding the precise flow of information is required for audits.

### 4. Integration with BI and Analytics Tools

Once the dependency graph is stored in Neo4j, it can be queried programmatically or connected to BI tools to generate reports, dashboards, or automated alerts. For example:

- Automatically notify analysts when upstream data changes
- Generate dependency tables for documentation
- Integrate lineage data into metrics tracking and observability pipelines

This makes it easier to maintain high-quality, trustworthy data across the organization.

### 5. Continuous Integration and Governance

`dbt-to-cypher` can be integrated into CI/CD pipelines. Every time new models are added or modified, the library can regenerate the Cypher scripts and update the graph database automatically. This ensures that your data lineage is always up-to-date and provides a single source of truth for governance and auditing. Benefits include:

- Automated checks for model and column consistency
- Improved collaboration between data engineering, analytics, and governance teams
- Faster onboarding for new projects or team members

This workflow enhances both reliability and transparency across data operations.

### Example Scenario

Consider a retail analytics team tracking sales metrics across multiple regions. Using `dbt-to-cypher`, they can:

1. Parse dbt models and catalog to generate a dependency graph.
2. Load the graph into Neo4j for visualization.
3. Identify which models contribute to monthly sales reports.
4. Trace specific columns to their source data for validation.
5. Update their CI/CD pipeline to regenerate lineage whenever dbt models are updated.

This approach not only simplifies debugging but also strengthens the organization’s confidence in its data quality and reporting accuracy.

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

## FAQ and Troubleshooting

### Q1: Why do I get errors when running `dbt-to-cypher`?

Common causes include missing `manifest.json` or `catalog.json` files. Make sure you run `dbt compile` and `dbt docs generate` in your project before using this library.

### Q2: Can I use `dbt-to-cypher` with partial dbt projects?

Yes, but some features like column-level lineage require complete model definitions. For partial projects, only model-level dependencies may be generated.

### Q3: Installation issues on Windows or Mac

Ensure your virtual environment is properly activated. Use the recommended `uv venv` workflow or a standard Python `venv`. Some OSes may require `python3 -m venv .venv` and activation through `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Linux/Mac).

### Q4: Performance tips

For large dbt projects, generating full column-level graphs can be resource-intensive. Consider filtering models or columns to focus on critical pipelines or using Neo4j’s batch import features for faster ingestion.

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

- [ ] Support for dbt sources and seeds
- [ ] Export to additional graph formats (GraphML, DOT)
- [ ] Support extracting model and column dependencies alone
- [ ] Support direct population of dependencies into a graph database (preferably Neo4j)
- [ ] Interactive visualization tools
- [ ] Support for dbt metrics and exposures

## Author

laphoang

## Acknowledgments

Built with modern Python packaging standards (PEP 621), uv for environment management, and best practices for Python libraries and data engineering workflows.
