"""
Module for building and managing dependency graphs.
"""

from typing import Any, Optional

import networkx as nx


class DependencyGraph:
    """
    Represents a dbt dependency graph with models and columns as nodes.

    This class uses NetworkX to build and manipulate the dependency graph,
    providing methods for analysis and traversal.
    """

    def __init__(self):
        """Initialize an empty dependency graph."""
        self.graph = nx.DiGraph()

    def add_model(self, model_name: str, metadata: Optional[dict] = None):
        """
        Add a model node to the graph.

        Args:
            model_name: Unique identifier for the model
            metadata: Additional model metadata
        """
        self.graph.add_node(model_name, node_type="model", **(metadata or {}))

    def add_column(self, model_name: str, column_name: str, metadata: Optional[dict] = None):
        """
        Add a column node to the graph and connect it to its parent model.

        Args:
            model_name: Name of the model the column belongs to
            column_name: Column name (without model prefix)
            metadata: Additional column metadata
        """
        column_id = f"{model_name}.{column_name}"
        self.graph.add_node(column_id, node_type="column", **(metadata or {}))
        # Ensure the model node exists and add an edge from model -> column
        if model_name not in self.graph:
            self.add_model(model_name)
        self.add_dependency(model_name, column_id, relationship="has_column")

    def add_dependency(self, source: str, target: str, relationship: str = "depends_on"):
        """
        Add a dependency edge between nodes.

        Args:
            source: Source node identifier
            target: Target node identifier
            relationship: Type of relationship
        """
        self.graph.add_edge(source, target, relationship=relationship)

    def get_upstream_dependencies(self, node: str) -> set[str]:
        """
        Get all upstream dependencies for a node.

        Args:
            node: Node identifier

        Returns:
            Set of upstream node identifiers
        """
        return set(self.graph.predecessors(node))

    def get_downstream_dependencies(self, node: str) -> set[str]:
        """
        Get all downstream dependencies for a node.

        Args:
            node: Node identifier

        Returns:
            Set of downstream node identifiers
        """
        return set(self.graph.successors(node))

    def to_dict(self) -> dict[str, Any]:
        """
        Export the graph as a dictionary.

        Returns:
            Dictionary representation of the graph
        """
        return nx.node_link_data(self.graph)  # type: ignore[no-any-return]
