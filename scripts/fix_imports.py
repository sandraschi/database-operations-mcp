"""
Script to update imports in tool files to use the correct relative imports.
"""

import re
from pathlib import Path


def update_imports(file_path: str):
    """Update imports in a single file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace imports from config.mcp_config
    content = re.sub(
        r"from \s*\.\.\.config\.mcp_config import mcp",
        "from ...config.mcp_config import mcp",
        content,
    )

    # Replace relative imports from help_tools
    content = re.sub(
        r"from \s*\.help_tools import HelpSystem", "from . import help_tools as HelpSystem", content
    )

    # Replace relative imports from init_tools
    content = re.sub(r"from \s*\.init_tools import", "from . import init_tools as", content)

    # Write the updated content back to the file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    """Update imports in all tool files."""
    tools_dir = Path("d:/Dev/repos/database-operations-mcp/src/database_operations_mcp/handlers")

    # List of tool files to update
    tool_files = [
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

    # Update each tool file
    for tool_file in tool_files:
        file_path = tools_dir / tool_file
        if file_path.exists():
            print(f"Updating imports in {file_path}")
            update_imports(str(file_path))

    print("Import updates complete!")


if __name__ == "__main__":
    main()
