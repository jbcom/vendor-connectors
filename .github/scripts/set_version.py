#!/usr/bin/env python3
"""Auto-version script: Updates version based on GitHub run number.

Uses CalVer format: YYYY.MM.BUILD_NUMBER
Example: 2025.11.42

This ensures:
- Every push to main gets a unique, incrementing version
- No manual version management needed
- No git tags required
- Always publishable to PyPI
"""
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def main():
    # Get GitHub run number (always incrementing)
    run_number = os.environ.get("GITHUB_RUN_NUMBER", "0")
    
    # Generate CalVer: YYYY.MM.BUILD
    now = datetime.now(timezone.utc)
    new_version = f"{now.year}.{now.month}.{run_number}"
    
    # Update __init__.py
    init_file = Path("src/directed_inputs_class/__init__.py")
    content = init_file.read_text()
    
    # Replace version line
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("__version__"):
            lines[i] = f'__version__ = "{new_version}"'
            break
    
    init_file.write_text("\n".join(lines))
    
    # Output for GitHub Actions
    print(f"VERSION={new_version}")
    
    # Set output for workflow
    if github_output := os.environ.get("GITHUB_OUTPUT"):
        with open(github_output, "a") as f:
            f.write(f"version={new_version}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
