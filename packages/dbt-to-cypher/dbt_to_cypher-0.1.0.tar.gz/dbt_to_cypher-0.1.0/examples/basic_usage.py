"""
Example: Basic usage of dbt-to-cypher library.

This example demonstrates how to:
1. Initialize the dependency extractor
2. Build a dependency graph manually
3. Generate Cypher queries
"""

from pathlib import Path

from dbt_to_cypher import CypherGenerator, DbtDependencyExtractor, DependencyGraph


def example_manual_graph():
    """Example: Manually building a dependency graph."""
    print("=" * 60)
    print("Example 1: Manually Building a Dependency Graph")
    print("=" * 60)

    # Create a new graph
    graph = DependencyGraph()

    # Add some models
    graph.add_model("stg_customers", {"schema": "staging", "database": "analytics"})
    graph.add_model("stg_orders", {"schema": "staging", "database": "analytics"})
    graph.add_model("customers", {"schema": "marts", "database": "analytics"})

    # Add columns
    graph.add_column("stg_customers", "customer_id", {"data_type": "integer"})
    graph.add_column("stg_customers", "first_name", {"data_type": "varchar"})
    graph.add_column("stg_orders", "order_id", {"data_type": "integer"})
    graph.add_column("stg_orders", "customer_id", {"data_type": "integer"})
    graph.add_column("customers", "customer_id", {"data_type": "integer"})

    # Add model dependencies
    graph.add_dependency("stg_customers", "customers", "depends_on")
    graph.add_dependency("stg_orders", "customers", "depends_on")

    # Add column dependencies
    graph.add_dependency("stg_customers.customer_id", "customers.customer_id", "derives_from")

    # Generate Cypher queries
    generator = CypherGenerator(graph)
    cypher_script = generator.generate_all_queries()

    print("\nGenerated Cypher Script:")
    print("-" * 60)
    print(cypher_script)
    print()


def example_extract_from_dbt():
    """Example: Extracting dependencies from a dbt project."""
    print("=" * 60)
    print("Example 2: Extracting from dbt Project")
    print("=" * 60)

    # This would require a real dbt project
    project_path = Path("./sample_dbt_project")

    if not project_path.exists():
        print(f"\n⚠️  Sample dbt project not found at {project_path}")
        print("This example requires a dbt project with manifest.json")
        return

    # Initialize extractor
    extractor = DbtDependencyExtractor(project_path)

    try:
        # Extract dependencies (this would work once implemented)
        dependencies = extractor.extract_all()
        print(f"\nExtracted dependencies: {dependencies}")
    except NotImplementedError:
        print("\n⚠️  Dependency extraction not yet implemented")
        print("This is a placeholder for future functionality")


def example_query_graph():
    """Example: Querying the dependency graph."""
    print("=" * 60)
    print("Example 3: Querying the Dependency Graph")
    print("=" * 60)

    # Build a sample graph
    graph = DependencyGraph()
    graph.add_model("raw_users")
    graph.add_model("stg_users")
    graph.add_model("dim_users")
    graph.add_dependency("raw_users", "stg_users")
    graph.add_dependency("stg_users", "dim_users")

    # Query upstream dependencies
    upstream = graph.get_upstream_dependencies("dim_users")
    print(f"\nUpstream dependencies of 'dim_users': {upstream}")

    # Query downstream dependencies
    downstream = graph.get_downstream_dependencies("raw_users")
    print(f"Downstream dependencies of 'raw_users': {downstream}")

    # Export graph as dictionary
    graph_dict = graph.to_dict()
    print(f"\nGraph structure: {len(graph_dict['nodes'])} nodes, {len(graph_dict['links'])} edges")


if __name__ == "__main__":
    example_manual_graph()
    print("\n")
    example_extract_from_dbt()
    print("\n")
    example_query_graph()
