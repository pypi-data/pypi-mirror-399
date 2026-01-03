#!/usr/bin/env python3
"""
Dual-Layer Provenance Tool

Commands:
    stamp <file>        Create timestamp proof
    verify <file.ots>   Verify existing proof
    install-hook        Set up git post-commit hook

Requires: pip install opentimestamps-client
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

VERSION = "1.0.0"


def stamp(filepath: str) -> bool:
    """Create an OpenTimestamps proof for a file."""
    if not Path(filepath).exists():
        print(f"Error: File not found: {filepath}")
        return False

    try:
        result = subprocess.run(
            ["ots", "stamp", filepath],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            ots_file = f"{filepath}.ots"
            print(f"Timestamp created: {ots_file}")
            print("Note: Full Bitcoin confirmation takes 1-24 hours.")
            return True
        else:
            print(f"Error: {result.stderr}")
            return False
    except FileNotFoundError:
        print("Error: OpenTimestamps client not found.")
        print("Install with: pip install opentimestamps-client")
        return False


def verify(ots_filepath: str) -> bool:
    """Verify an OpenTimestamps proof."""
    if not Path(ots_filepath).exists():
        print(f"Error: File not found: {ots_filepath}")
        return False

    try:
        result = subprocess.run(
            ["ots", "verify", ots_filepath],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode == 0
    except FileNotFoundError:
        print("Error: OpenTimestamps client not found.")
        print("Install with: pip install opentimestamps-client")
        return False


def install_hook() -> bool:
    """Install git post-commit hook for automatic timestamping."""
    git_dir = Path(".git")
    if not git_dir.exists():
        print("Error: Not a git repository.")
        return False

    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)

    hook_path = hooks_dir / "post-commit"

    hook_content = '''#!/bin/sh
# Dual-Layer Provenance: Auto-timestamp commits

COMMIT=$(git rev-parse HEAD)
OTS_DIR=".ots_proofs"

mkdir -p "$OTS_DIR"
echo "$COMMIT $(date -Iseconds)" > "$OTS_DIR/$COMMIT.txt"

if command -v ots &> /dev/null; then
    ots stamp "$OTS_DIR/$COMMIT.txt" 2>/dev/null
    echo "Timestamped commit: $COMMIT"
fi
'''

    with open(hook_path, 'w', newline='\n') as f:
        f.write(hook_content)

    # Make executable (on Unix-like systems)
    try:
        os.chmod(hook_path, 0o755)
    except:
        pass  # Windows doesn't need this

    print(f"Git hook installed: {hook_path}")
    print("Future commits will be automatically timestamped.")
    return True


def main():
    if len(sys.argv) < 2:
        print(f"Dual-Layer Provenance v{VERSION}")
        print()
        print("Usage:")
        print("  python caprazli_provenance.py stamp <file>")
        print("  python caprazli_provenance.py verify <file.ots>")
        print("  python caprazli_provenance.py install-hook")
        print()
        print("Documentation: https://doi.org/10.5281/zenodo.18115235")
        return 1

    command = sys.argv[1].lower()

    if command == "stamp":
        if len(sys.argv) < 3:
            print("Error: Please specify a file to stamp.")
            return 1
        return 0 if stamp(sys.argv[2]) else 1

    elif command == "verify":
        if len(sys.argv) < 3:
            print("Error: Please specify an .ots file to verify.")
            return 1
        return 0 if verify(sys.argv[2]) else 1

    elif command == "install-hook":
        return 0 if install_hook() else 1

    else:
        print(f"Unknown command: {command}")
        print("Use: stamp, verify, or install-hook")
        return 1


if __name__ == "__main__":
    sys.exit(main())
