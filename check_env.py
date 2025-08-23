#!/usr/bin/env python3
"""Check Python environment and paths."""
import sys
import os
import platform

print("=== Python Environment ===")
print(f"Python executable: {sys.executable}")
print(f"Python version: {platform.python_version()}")
print(f"Platform: {platform.platform()}")
print(f"Current working directory: {os.getcwd()}")

print("\n=== Python Path ===")
for path in sys.path:
    print(f"- {path}")

print("\n=== Environment Variables ===")
for key, value in os.environ.items():
    if 'PYTHON' in key.upper() or 'PATH' in key.upper():
        print(f"{key}={value}")

print("\n=== Test Import ===")
try:
    import database_operations_mcp
    print("✅ Successfully imported database_operations_mcp")
    print(f"Version: {getattr(database_operations_mcp, '__version__', 'unknown')}")
except ImportError as e:
    print(f"❌ Failed to import database_operations_mcp: {e}")
    print("\nTroubleshooting steps:")
    print("1. Make sure you're in the project root directory")
    print("2. Run: pip install -e .")
    print("3. Check that the src directory is in your PYTHONPATH")
