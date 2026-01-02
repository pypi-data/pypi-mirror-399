"""Tests for the CypherGenerator class."""

from dbt_to_cypher.cypher import CypherGenerator
from dbt_to_cypher.graph import DependencyGraph


def test_generator_initialization():
    """Test that the generator initializes with a graph."""
    graph = DependencyGraph()
    generator = CypherGenerator(graph)

    assert generator.graph == graph


def test_generate_node_queries_empty():
    """Test generating node queries for an empty graph."""
    graph = DependencyGraph()
    generator = CypherGenerator(graph)

    queries = generator.generate_node_queries()
    assert queries == []


def test_generate_model_node_query():
    """Test generating a Cypher query for a model node."""
    graph = DependencyGraph()
    graph.add_model("my_model", {"schema": "public"})
    generator = CypherGenerator(graph)

    queries = generator.generate_node_queries()
    assert len(queries) == 1
    assert "MERGE (m:Model {name: 'my_model'" in queries[0]


def test_generate_column_node_query():
    """Test generating a Cypher query for a column node."""
    graph = DependencyGraph()
    graph.add_model("my_model")
    graph.add_column("my_model", "my_column")
    generator = CypherGenerator(graph)

    queries = generator.generate_node_queries()
    # Should have 2 nodes: model and column
    assert len(queries) == 2


def test_generate_relationship_queries():
    """Test generating relationship queries."""
    graph = DependencyGraph()
    graph.add_model("model_a")
    graph.add_model("model_b")
    graph.add_dependency("model_a", "model_b", "depends_on")
    generator = CypherGenerator(graph)

    queries = generator.generate_relationship_queries()
    assert len(queries) == 1
    assert "DEPENDS_ON" in queries[0]


def test_generate_all_queries():
    """Test generating all queries as a complete script."""
    graph = DependencyGraph()
    graph.add_model("model_a")
    graph.add_model("model_b")
    graph.add_dependency("model_a", "model_b")
    generator = CypherGenerator(graph)

    script = generator.generate_all_queries()
    assert isinstance(script, str)
    assert "MERGE" in script
    assert script.endswith(";")
