"""
Setup script to help with initial project installation.
Run this after cloning the repository.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n{'=' * 60}")
    print(f"📦 {description}")
    print(f"{'=' * 60}")
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with error: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        return False


def main():
    """Run the setup process."""
    print("\n" + "=" * 60)
    print("🚀 dbt-to-cypher Development Environment Setup")
    print("=" * 60)

    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Error: pyproject.toml not found!")
        print("Please run this script from the project root directory.")
        sys.exit(1)

    steps = [
        ([sys.executable, "-m", "pip", "install", "uv"], "Installing uv package manager"),
        (["uv", "venv"], "Creating virtual environment"),
        (["uv", "pip", "install", "-e", ".[dev]"], "Installing project dependencies"),
        (["pre-commit", "install"], "Installing pre-commit hooks"),
    ]

    failed_steps = []

    for cmd, description in steps:
        if not run_command(cmd, description):
            failed_steps.append(description)

    print("\n" + "=" * 60)
    if not failed_steps:
        print("✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Activate the virtual environment:")
        print("   - Windows: .venv\\Scripts\\activate")
        print("   - Linux/Mac: source .venv/bin/activate")
        print("\n2. Run tests: pytest")
        print("3. Start developing!")
    else:
        print("⚠️  Setup completed with some errors:")
        for step in failed_steps:
            print(f"   - {step}")
        print("\nPlease check the errors above and fix them manually.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
