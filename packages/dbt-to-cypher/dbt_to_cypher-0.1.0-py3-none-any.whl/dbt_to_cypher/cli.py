"""
Command-line interface for dbt-to-cypher.
"""

import argparse
import logging
import sys
from pathlib import Path

from dbt_to_cypher import __version__
from dbt_to_cypher.dbt_to_cypher import extract_dbt_project

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Extract dbt dependencies and convert to Cypher queries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"dbt-to-cypher {__version__}",
    )

    parser.add_argument(
        "project_path",
        type=Path,
        help="Path to the dbt project directory",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file for Cypher queries (default: stdout)",
    )

    args = parser.parse_args()

    try:
        cypher_script = extract_dbt_project(args.project_path, args.output)
        logger.info(cypher_script)
        return 0

    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
