#!/usr/bin/env python3
"""Quick test script to verify database_operations package structure."""

import sys

sys.path.insert(0, "src")

try:
    print("Testing database_operations import...")
    import database_operations

    print("✅ database_operations package imported successfully")

    print("Testing main module import...")
    from database_operations.main import main

    print("✅ main function imported successfully")

    print("Testing database_manager import...")
    from database_operations.database_manager import BaseDatabaseConnector, DatabaseType

    print("✅ database_manager classes imported successfully")

    print("Testing handlers import...")
    from database_operations.handlers import connection_tools

    print("✅ handlers imported successfully")

    print("\n🎯 ALL IMPORTS SUCCESSFUL - Package structure is correct!")

except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback

    traceback.print_exc()
except Exception as e:
    print(f"❌ Other error: {e}")
    import traceback

    traceback.print_exc()
