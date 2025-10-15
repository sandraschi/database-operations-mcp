#!/usr/bin/env python3
"""Minimal test script for FastMCP import."""

import os
import sys


def main():
    try:
        # Add src to path
        project_root = os.path.dirname(os.path.abspath(__file__))
        src_path = os.path.join(project_root, "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        print("Python path:")
        for p in sys.path:
            print(f"- {p}")

        print("\nAttempting to import FastMCP...")
        import fastmcp

        print(f"✅ FastMCP imported successfully (version: {fastmcp.__version__})")

        print("\nAttempting to import database_operations_mcp...")
        print("✅ database_operations_mcp imported successfully")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
