"""
Core module for dbt-to-cypher conversion.

This module provides the main API for extracting dbt dependencies and generating Cypher queries.
"""

import logging
from pathlib import Path
from typing import Any, Optional, Union

from dbt_to_cypher.cypher import CypherGenerator
from dbt_to_cypher.extractor import DbtDependencyExtractor
from dbt_to_cypher.graph import DependencyGraph

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def extract_dependencies(project_path: Union[Path, str]) -> dict[str, Any]:
    """
    Extract all dependencies from a dbt project.

    Args:
        project_path: Path to the dbt project directory

    Returns:
        Dictionary containing models, columns, model_dependencies, and column_dependencies
    """
    extractor = DbtDependencyExtractor(str(project_path))
    return extractor.extract_all()


def build_dependency_graph(dependencies: dict[str, Any]) -> DependencyGraph:
    """
    Build a dependency graph from extracted dependencies.

    Args:
        dependencies: Dictionary of dependencies from extract_dependencies()

    Returns:
        DependencyGraph instance
    """
    graph = DependencyGraph()

    # Add model nodes
    models = dependencies.get("models", {}) if isinstance(dependencies, dict) else {}
    for model, model_data in models.items():
        graph.add_model(model, metadata=model_data)

    # Add column nodes
    columns = dependencies.get("columns", {}) if isinstance(dependencies, dict) else {}
    for column, col_data in columns.items():
        model_name = col_data.get("model_name", "")
        if model_name:
            # Extract column name from full identifier (e.g., "model.column" -> "column")
            col_name = column.split(".")[-1] if "." in column else column
            graph.add_column(model_name, col_name, metadata=col_data)

    # Add model-level dependencies
    model_dependencies = (
        dependencies.get("model_dependencies", {}) if isinstance(dependencies, dict) else {}
    )
    for model, upstreams in model_dependencies.items():
        for upstream in upstreams:
            graph.add_dependency(model, upstream)

    # Add column-level dependencies
    column_dependencies = (
        dependencies.get("column_dependencies", {}) if isinstance(dependencies, dict) else {}
    )
    for column, upstreams in column_dependencies.items():
        for upstream in upstreams:
            graph.add_dependency(column, upstream)

    return graph


def generate_cypher_queries(graph: DependencyGraph) -> str:
    """
    Generate Cypher queries from a dependency graph.

    Args:
        graph: DependencyGraph instance

    Returns:
        Cypher query script as a string
    """
    generator = CypherGenerator(graph)
    return generator.generate_all_queries()


def extract_dbt_project(
    project_path: Union[Path, str],
    output_path: Optional[Union[Path, str]] = None,
) -> str:
    """
    Main process: extract dbt dependencies, build graph, and generate Cypher.

    Args:
        project_path: Path to the dbt project directory
        output_path: Optional path to write Cypher queries to file

    Returns:
        Cypher query script as a string
    """
    logger.info(f"Loading dbt project from: {project_path}")

    # Extract dependencies
    dependencies = extract_dependencies(project_path)

    # Build graph
    graph = build_dependency_graph(dependencies)

    # Generate Cypher
    cypher_script = generate_cypher_queries(graph)

    # Optionally write to file
    if output_path:
        Path(output_path).write_text(cypher_script)
        logger.info(f"Cypher queries written to {output_path}")
    else:
        logger.info("Cypher queries generated successfully")

    return cypher_script
