#!/usr/bin/env python3
"""
Update version across all files in the project.

Usage:
    python scripts/update_version.py 0.1.0
"""

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def update_version(new_version: str) -> None:
    """Update version in pyproject.toml and peak_locator/__init__.py."""
    # Validate version format (basic check)
    if not re.match(r'^\d+\.\d+\.\d+', new_version):
        raise ValueError(f"Invalid version format: {new_version}. Expected format: X.Y.Z")

    # Update pyproject.toml
    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    content = pyproject_path.read_text()
    content = re.sub(
        r'^version = ".*"',
        f'version = "{new_version}"',
        content,
        flags=re.MULTILINE
    )
    pyproject_path.write_text(content)
    print(f"✓ Updated version in pyproject.toml to {new_version}")

    # Update peak_locator/__init__.py
    init_path = PROJECT_ROOT / "peakfinder" / "__init__.py"
    content = init_path.read_text()
    content = re.sub(
        r'^__version__ = ".*"',
        f'__version__ = "{new_version}"',
        content,
        flags=re.MULTILINE
    )
    init_path.write_text(content)
    print(f"✓ Updated version in peak_locator/__init__.py to {new_version}")

    print(f"\nVersion updated to {new_version} successfully!")
    print("\nNext steps:")
    print("  1. Review the changes")
    print("  2. Commit: git commit -am 'chore: bump version to {new_version}'")
    print("  3. Tag: git tag -a v{new_version} -m 'Release {new_version}'")
    print("  4. Push: git push && git push --tags")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/update_version.py <version>")
        print("Example: python scripts/update_version.py 0.1.0")
        sys.exit(1)

    version = sys.argv[1]
    try:
        update_version(version)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

