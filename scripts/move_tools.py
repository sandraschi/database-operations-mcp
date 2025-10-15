"""
Script to move tool modules to the tools directory and update imports.
"""

import shutil
from pathlib import Path

# Define the source and target directories
SRC_DIR = Path(r"d:\Dev\repos\database-operations-mcp\src\database_operations_mcp\handlers")
TARGET_DIR = SRC_DIR / "tools"

# List of tool modules to move
TOOL_MODULES = [
    "calibre_tools.py",
    "connection_tools.py",
    "data_tools.py",
    "fts_tools.py",
    "help_tools.py",
    "init_tools.py",
    "management_tools.py",
    "media_tools.py",
    "plex_tools.py",
    "query_tools.py",
    "registry_tools.py",
    "schema_tools.py",
    "windows_tools.py",
]


def move_tool_modules():
    """Move tool modules to the tools directory."""
    # Ensure the target directory exists
    TARGET_DIR.mkdir(exist_ok=True, parents=True)

    moved_files = []

    # Move each tool module
    for module in TOOL_MODULES:
        src = SRC_DIR / module
        if src.exists():
            dest = TARGET_DIR / module
            shutil.move(str(src), str(dest))
            moved_files.append(module)

    return moved_files


if __name__ == "__main__":
    print(f"Moving tool modules to {TARGET_DIR}...")
    moved = move_tool_modules()
    print(f"Moved {len(moved)} tool modules:")
    for module in moved:
        print(f"- {module}")
    print("\nDon't forget to update imports in the affected files!")
