"""Tests for the dbt_to_cypher module."""

from dbt_to_cypher.dbt_to_cypher import (
    build_dependency_graph,
    generate_cypher_queries,
)
from dbt_to_cypher.graph import DependencyGraph


def test_build_dependency_graph_empty():
    """Test building a graph from empty dependencies."""
    dependencies = {
        "models": {},
        "columns": {},
        "model_dependencies": {},
        "column_dependencies": {},
    }
    graph = build_dependency_graph(dependencies)

    assert isinstance(graph, DependencyGraph)
    assert len(graph.graph.nodes) == 0
    assert len(graph.graph.edges) == 0


def test_build_dependency_graph_with_models():
    """Test building a graph with models."""
    dependencies = {
        "models": {
            "model_a": {"name": "model_a", "schema": "public"},
            "model_b": {"name": "model_b", "schema": "public"},
        },
        "columns": {},
        "model_dependencies": {"model_a": ["model_b"]},
        "column_dependencies": {},
    }
    graph = build_dependency_graph(dependencies)

    assert len(graph.graph.nodes) == 2
    assert "model_a" in graph.graph.nodes
    assert "model_b" in graph.graph.nodes
    assert graph.graph.has_edge("model_a", "model_b")


def test_build_dependency_graph_with_columns():
    """Test building a graph with models and columns."""
    dependencies = {
        "models": {"my_model": {"name": "my_model", "schema": "public"}},
        "columns": {
            "my_model.col1": {"name": "my_model.col1", "model_name": "my_model"},
            "my_model.col2": {"name": "my_model.col2", "model_name": "my_model"},
        },
        "model_dependencies": {},
        "column_dependencies": {},
    }
    graph = build_dependency_graph(dependencies)

    assert len(graph.graph.nodes) == 3  # 1 model + 2 columns
    assert "my_model" in graph.graph.nodes
    assert "my_model.col1" in graph.graph.nodes
    assert "my_model.col2" in graph.graph.nodes
    # Check model -> column edges
    assert graph.graph.has_edge("my_model", "my_model.col1")
    assert graph.graph.has_edge("my_model", "my_model.col2")


def test_generate_cypher_queries_empty():
    """Test generating Cypher from an empty graph."""
    graph = DependencyGraph()
    cypher_script = generate_cypher_queries(graph)

    assert isinstance(cypher_script, str)
    assert len(cypher_script) >= 0


def test_generate_cypher_queries_with_models():
    """Test generating Cypher with models."""
    graph = DependencyGraph()
    graph.add_model("model_a")
    graph.add_model("model_b")
    graph.add_dependency("model_a", "model_b")

    cypher_script = generate_cypher_queries(graph)

    assert isinstance(cypher_script, str)
    assert "Model" in cypher_script or "model" in cypher_script.lower()
