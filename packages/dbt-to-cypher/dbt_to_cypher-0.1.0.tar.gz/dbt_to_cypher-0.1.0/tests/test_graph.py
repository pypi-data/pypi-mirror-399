"""Tests for the DependencyGraph class."""

from dbt_to_cypher.graph import DependencyGraph


def test_graph_initialization():
    """Test that the graph initializes empty."""
    graph = DependencyGraph()
    assert len(graph.graph.nodes) == 0
    assert len(graph.graph.edges) == 0


def test_add_model():
    """Test adding a model node."""
    graph = DependencyGraph()
    graph.add_model("my_model", {"description": "Test model"})

    assert "my_model" in graph.graph.nodes
    assert graph.graph.nodes["my_model"]["node_type"] == "model"
    assert graph.graph.nodes["my_model"]["description"] == "Test model"


def test_add_column():
    """Test adding a column node."""
    graph = DependencyGraph()
    graph.add_model("my_model")
    graph.add_column("my_model", "my_column", {"data_type": "varchar"})

    column_id = "my_model.my_column"
    assert column_id in graph.graph.nodes
    assert graph.graph.nodes[column_id]["node_type"] == "column"
    assert graph.graph.nodes[column_id]["data_type"] == "varchar"

    # Check that edge exists from model to column
    assert graph.graph.has_edge("my_model", column_id)


def test_add_dependency():
    """Test adding a dependency edge."""
    graph = DependencyGraph()
    graph.add_model("model_a")
    graph.add_model("model_b")
    graph.add_dependency("model_a", "model_b")

    assert graph.graph.has_edge("model_a", "model_b")


def test_get_upstream_dependencies():
    """Test getting upstream dependencies."""
    graph = DependencyGraph()
    graph.add_model("model_a")
    graph.add_model("model_b")
    graph.add_model("model_c")
    graph.add_dependency("model_a", "model_c")
    graph.add_dependency("model_b", "model_c")

    upstream = graph.get_upstream_dependencies("model_c")
    assert upstream == {"model_a", "model_b"}


def test_get_downstream_dependencies():
    """Test getting downstream dependencies."""
    graph = DependencyGraph()
    graph.add_model("model_a")
    graph.add_model("model_b")
    graph.add_model("model_c")
    graph.add_dependency("model_a", "model_b")
    graph.add_dependency("model_a", "model_c")

    downstream = graph.get_downstream_dependencies("model_a")
    assert downstream == {"model_b", "model_c"}
