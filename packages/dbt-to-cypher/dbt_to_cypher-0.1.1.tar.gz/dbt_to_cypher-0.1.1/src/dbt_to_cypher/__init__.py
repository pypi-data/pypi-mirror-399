"""
dbt-to-cypher: Extract dependency graphs from dbt and convert to Cypher queries.

This library provides tools to parse dbt projects, extract model and column-level
dependencies, and generate Cypher queries for visualization and analysis in graph databases.
"""

__version__ = "0.1.0"

from dbt_to_cypher.cypher import CypherGenerator
from dbt_to_cypher.dbt_to_cypher import extract_dbt_project, extract_dependencies
from dbt_to_cypher.extractor import DbtDependencyExtractor
from dbt_to_cypher.graph import DependencyGraph

__all__ = [
    "DbtDependencyExtractor",
    "DependencyGraph",
    "CypherGenerator",
    "extract_dbt_project",
    "extract_dependencies",
]
