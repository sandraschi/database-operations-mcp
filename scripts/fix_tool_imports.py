"""
Script to fix imports in tool modules after moving to tools directory.
"""

import re
from pathlib import Path

TOOLS_DIR = Path(r"d:\Dev\repos\database-operations-mcp\src\database_operations_mcp\handlers\tools")

# List of all tool modules
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


def update_file_imports(file_path: Path):
    """Update imports in a single file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Pattern to match 'from . import module' or 'from ..module import something'
    pattern = r"^from\s+(\.+)\s+import\s+([\w\s,]+)$"

    def replace_import(match):
        relative_import = match.group(1).strip()
        modules = [m.strip() for m in match.group(2).split(",")]

        # Check if any of the imported modules are in our tools directory
        tool_imports = [m for m in modules if m in [mod[:-3] for mod in TOOL_MODULES]]

        if tool_imports:
            if relative_import == ".":
                # Change 'from . import x' to 'from .tools import x'
                new_import = f"from . import {match.group(2)}"
                print(f"Updating import in {file_path.name}: {match.group(0)} -> {new_import}")
                return new_import
            elif relative_import == "..":
                # Change 'from ..module import x' to 'from ..tools.module import x'
                new_import = f"from ..tools import {match.group(2)}"
                print(f"Updating import in {file_path.name}: {match.group(0)} -> {new_import}")
                return new_import

        return match.group(0)

    # Apply the replacement
    new_content = re.sub(pattern, replace_import, content, flags=re.MULTILINE)

    # Also handle direct imports like 'import module'
    for module in [m[:-3] for m in TOOL_MODULES]:
        pattern = rf"^import\s+{module}\s*$"
        if re.search(pattern, new_content, re.MULTILINE):
            new_content = re.sub(
                pattern, f"from . import {module}", new_content, flags=re.MULTILINE
            )
            print(  # noqa: E501
                f"Updated direct import in {file_path.name}: "
                f"import {module} -> from . import {module}"
            )

    # Write the updated content back to the file
    if new_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True

    return False


def main():
    """Update imports in all tool modules."""
    updated_files = []

    for module in TOOL_MODULES:
        file_path = TOOLS_DIR / module
        if file_path.exists():
            if update_file_imports(file_path):
                updated_files.append(module)

    print(f"\nUpdated imports in {len(updated_files)} files:")
    for module in updated_files:
        print(f"- {module}")


if __name__ == "__main__":
    main()
