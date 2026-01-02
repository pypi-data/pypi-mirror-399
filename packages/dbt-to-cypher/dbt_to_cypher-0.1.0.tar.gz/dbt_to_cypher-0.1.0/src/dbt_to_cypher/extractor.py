"""
Module for extracting dependencies from dbt projects.
"""

import json
from pathlib import Path
from typing import Any

from dbt_artifacts_parser.parser import parse_catalog, parse_manifest
from dbt_colibri.lineage_extractor.extractor import DbtColumnLineageExtractor


class DbtDependencyExtractor:
    """
    Extract model and column-level dependencies from a dbt project.

    This class parses dbt manifest.json and other project files to build
    a comprehensive dependency graph including both model-level and
    column-level lineage.
    """

    def __init__(self, project_path: str):
        """
        Initialize the extractor with a dbt project path.

        Args:
            project_path: Path to the dbt project directory
        """
        self.project_path = Path(project_path)
        self.manifest_path = self.project_path / "target" / "manifest.json"
        self.catalog_path = self.project_path / "target" / "catalog.json"
        self.manifest: Any
        self.catalog: Any

    def load_file(self) -> None:
        """
        Load a dbt JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            Dictionary containing the parsed JSON data

        Raises:
            FileNotFoundError: If the file does not exist
            json.JSONDecodeError: If the file is not valid JSON
        """
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"File not found: {self.manifest_path}")
        if not self.catalog_path.exists():
            raise FileNotFoundError(f"File not found: {self.catalog_path}")

        with open(self.manifest_path, encoding="utf-8") as fp:
            manifest_dict = json.load(fp)

            # Filter out test nodes to avoid Pydantic validation errors in dbt-artifacts-parser, remove after dbt-artifacts-parser fix
            if "nodes" in manifest_dict:
                manifest_dict["nodes"] = {
                    k: v for k, v in manifest_dict["nodes"].items() if not k.startswith("test.")
                }

            self.manifest = parse_manifest(manifest=manifest_dict)

        with open(self.catalog_path, encoding="utf-8") as fp:
            catalog_dict = json.load(fp)

            # Remove extra metadata fields to avoid Pydantic validation errors in dbt-artifacts-parser, remove after dbt-artifacts-parser fix
            if "metadata" in catalog_dict:
                if "invocation_started_at" in catalog_dict["metadata"]:
                    del catalog_dict["metadata"]["invocation_started_at"]

            self.catalog = parse_catalog(catalog=catalog_dict)

        return

    def extract_columns(self) -> dict[str, Any]:
        """
        Extract columns from the dbt project.

        Returns:
            Dictionary containing column information
        """
        nodes: dict[str, Any] = {}
        for node_id, catalog_node in self.catalog.nodes.items():
            # Get catalog columns for this node
            columns = getattr(catalog_node, "columns", {}) or {}

            for column_name, column in columns.items():
                # Convert column to dict and add computed fields
                name = f"{node_id}.{column_name}"
                column_dict = (
                    column.model_dump()
                    if hasattr(column, "model_dump")
                    else (column.dict() if hasattr(column, "dict") else dict(column))
                )
                column_dict["name"] = name
                column_dict["model_name"] = node_id
                nodes[name] = column_dict

        return nodes

    def extract_models(self) -> dict[str, Any]:
        """
        Extract models from the dbt project.

        Returns:
            Dictionary containing model information
        """
        nodes: dict[str, Any] = {}
        for node_id, node in self.manifest.nodes.items():
            # Get catalog columns for this node
            catalog_node = self.catalog.nodes.get(node_id)
            columns = getattr(catalog_node, "columns", {}) or {}

            # Build a minimal node dict containing only the selected attributes
            db = getattr(node, "database", None) or getattr(node, "database_name", None)
            schema = getattr(node, "schema_", None) or getattr(node, "schema", None)
            name = getattr(node, "name", None)

            node_dict: dict[str, Any] = {
                "fqn": f"{db}.{schema}.{name}",
                "materialization": getattr(getattr(node, "config", None), "materialized", None),
                "database": db,
                "schema": schema,
                "resource_type": getattr(node, "resource_type", None),
                # "compiled_code": getattr(node, "compiled_code", None),
                "columns": columns,
            }

            nodes[node_id] = node_dict

        return nodes

    def extract_model_dependencies(self) -> dict[str, Any]:
        """
        Extract model-level dependencies from the dbt project.

        Returns:
            Dictionary containing model dependency information
        """
        dependencies: dict[str, Any] = {}
        for node_id, node in self.manifest.nodes.items():
            dependencies[node_id] = node.depends_on.nodes

        return dependencies

    def extract_column_dependencies(self) -> dict[str, list[str]]:
        """
        Extract column-level dependencies from the dbt project.

        Returns:
            Dictionary mapping column FQN to list of dependent column FQNs.
            Format: {"model.package.model_name.column_name": ["upstream_model.column_name", ...]}
        """
        extractor = DbtColumnLineageExtractor(self.manifest_path, self.catalog_path)
        lineage = extractor.build_lineage_map()

        # Transform lineage into column: [depends_on_columns] format
        column_dependencies: dict[str, list[str]] = {}

        for model_id, columns in lineage.items():
            for column_name, node in columns.items():
                # Build the full column identifier
                column_fqn = f"{model_id}.{column_name}"

                # Extract upstream column dependencies
                upstream_columns = []
                if hasattr(node, "downstream") and node.downstream:
                    for downstream_node in node.downstream:
                        if hasattr(downstream_node, "name") and downstream_node.name:
                            # The name contains the column name with the table alias
                            # Example: "model_1.customer_id" or "a.first_name"
                            parts = downstream_node.name.split(".")
                            if len(parts) == 2:
                                table_ref, col_name = parts

                                # Extract model reference from the downstream node's table expression
                                if hasattr(downstream_node, "expression"):
                                    expr = downstream_node.expression
                                    # Try to get the actual table/model name
                                    if hasattr(expr, "this") and hasattr(expr.this, "this"):
                                        table_name = str(expr.this.this)

                                        # Find the corresponding model_id for this table reference
                                        for mid in lineage.keys():
                                            if mid.endswith(f".{table_name}"):
                                                upstream_columns.append(f"{mid}.{col_name}")
                                                break

                column_dependencies[column_fqn] = upstream_columns

        return column_dependencies

    def extract_all(self) -> dict:
        """
        Extract both model and column-level dependencies.

        Returns:
            Complete dependency graph data structure
        """
        # Ensure manifest/catalog are loaded before extracting
        if not getattr(self, "manifest", None) or not getattr(self, "catalog", None):
            self.load_file()

        return {
            "models": self.extract_models(),
            "columns": self.extract_columns(),
            "model_dependencies": self.extract_model_dependencies(),
            "column_dependencies": self.extract_column_dependencies(),
        }
