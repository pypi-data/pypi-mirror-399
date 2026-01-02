"""Tests for the DbtDependencyExtractor class."""

from pathlib import Path

from dbt_to_cypher.extractor import DbtDependencyExtractor


def test_extractor_initialization():
    """Test that the extractor initializes correctly."""
    project_path = Path("/fake/project")
    extractor = DbtDependencyExtractor(project_path)

    assert extractor.project_path == project_path
    assert extractor.manifest_path == project_path / "target" / "manifest.json"
    assert extractor.catalog_path == project_path / "target" / "catalog.json"
