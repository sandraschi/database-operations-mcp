#!/usr/bin/env python3
"""
List available databases for Database Operations MCP
"""

import sys

# Add src to path
sys.path.insert(0, "src")

from database_operations_mcp.database_manager import get_supported_databases


def main():
    databases = get_supported_databases()

    print("=== Database Operations MCP - Available Databases ===")
    print("")
    print("Supported database types:")

    # Group by category
    categories = {}
    for db in databases:
        category = db.get("category", "Other")
        if category not in categories:
            categories[category] = []
        categories[category].append(db)

    for category, dbs in categories.items():
        print(f"\n{category.upper()}:")
        for db in dbs:
            name = db.get("name", "Unknown")
            description = db.get("description", "")
            print(f"  • {name}: {description}")

    print(f"\nTotal supported database types: {len(databases)}")
    print("")
    print("STATUS: No databases are currently registered.")
    print("")
    print('To connect to a database, use the db_connection tool with operation "register"')


if __name__ == "__main__":
    main()
