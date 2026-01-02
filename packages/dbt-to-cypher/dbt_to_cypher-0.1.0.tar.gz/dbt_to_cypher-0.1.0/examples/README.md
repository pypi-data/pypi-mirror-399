# Examples

This directory contains example scripts demonstrating how to use the dbt-to-cypher library.

## Running Examples

Make sure you have installed the package in development mode:

```bash
uv pip install -e ".[dev]"
```

Then run any example:

```bash
python examples/basic_usage.py
```

## Available Examples

- `basic_usage.py` - Demonstrates core functionality including:
  - Building dependency graphs manually
  - Extracting dependencies from dbt projects
  - Querying the graph
  - Generating Cypher queries

## Creating Your Own Examples

Feel free to add your own example scripts here. Follow the pattern:

1. Import the necessary components
2. Demonstrate a specific use case
3. Include helpful comments and print statements
4. Add documentation to this README
