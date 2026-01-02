"""
Module for generating Cypher queries from dependency graphs.
"""

from dbt_to_cypher.graph import DependencyGraph


class CypherGenerator:
    """
    Generate Cypher queries from a dbt dependency graph.

    This class converts the dependency graph structure into Cypher CREATE
    and MERGE statements for loading into Neo4j or other graph databases.
    """

    def __init__(self, graph: DependencyGraph):
        """
        Initialize the generator with a dependency graph.

        Args:
            graph: DependencyGraph instance to convert
        """
        self.graph = graph

    def generate_node_queries(self) -> list[str]:
        """
        Generate Cypher queries to create nodes.

        Returns:
            List of Cypher CREATE/MERGE statements for nodes
        """
        queries = []

        for node, attrs in self.graph.graph.nodes(data=True):
            node_type = attrs.get("node_type", "unknown")

            if node_type == "model":
                query = self._generate_model_node_query(node, attrs)
            elif node_type == "column":
                query = self._generate_column_node_query(node, attrs)
            else:
                continue

            queries.append(query)

        return queries

    def generate_relationship_queries(self) -> list[str]:
        """
        Generate Cypher queries to create relationships.

        Returns:
            List of Cypher MERGE statements for relationships
        """
        queries = []

        for source, target, attrs in self.graph.graph.edges(data=True):
            relationship = attrs.get("relationship", "DEPENDS_ON")
            query = self._generate_relationship_query(source, target, relationship)
            queries.append(query)

        return queries

    def generate_all_queries(self) -> str:
        """
        Generate complete Cypher script for the entire graph.

        Returns:
            Complete Cypher script as a string
        """
        node_queries = self.generate_node_queries()
        relationship_queries = self.generate_relationship_queries()

        all_queries = node_queries + relationship_queries
        return ";\n".join(all_queries) + ";"

    def _generate_model_node_query(self, node_id: str, attrs: dict) -> str:
        """Generate Cypher for a model node."""
        props = self._format_properties(attrs)
        return f"MERGE (m:Model {{name: '{node_id}'{props}}})"

    def _generate_column_node_query(self, node_id: str, attrs: dict) -> str:
        """Generate Cypher for a column node."""
        props = self._format_properties(attrs)
        return f"MERGE (c:Column {{id: '{node_id}'{props}}})"

    def _generate_relationship_query(self, source: str, target: str, rel_type: str) -> str:
        """Generate Cypher for a relationship."""
        rel_type_upper = rel_type.upper().replace(" ", "_")
        return (
            f"MATCH (s {{name: '{source}'}}), (t {{name: '{target}'}}) "
            f"MERGE (s)-[:{rel_type_upper}]->(t)"
        )

    def _format_properties(self, attrs: dict) -> str:
        """Format node properties for Cypher."""
        # Filter out non-serializable or internal properties
        exclude_keys = {"node_type"}
        props = {
            k: v
            for k, v in attrs.items()
            if k not in exclude_keys and isinstance(v, (str, int, float, bool))
        }

        if not props:
            return ""

        prop_strings = [
            f", {k}: '{v}'" if isinstance(v, str) else f", {k}: {v}" for k, v in props.items()
        ]
        return "".join(prop_strings)
