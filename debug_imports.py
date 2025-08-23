#!/usr/bin/env python3
"""Debug script for import issues."""
import sys
import os
import importlib

def check_import(module_name):
    """Check if a module can be imported."""
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, '__version__', 'version not found')
        print(f"✅ {module_name} imported successfully (version: {version})")
        return True
    except ImportError as e:
        print(f"❌ Failed to import {module_name}: {e}")
        return False
    except Exception as e:
        print(f"⚠️  Error importing {module_name}: {e}")
        return False

def main():
    """Main function to test imports."""
    print("=== Python Environment ===")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    
    print("\n=== Python Path ===")
    for path in sys.path:
        print(f"- {path}")
    
    print("\n=== Testing Imports ===")
    modules = [
        'fastmcp',
        'pydantic',
        'sqlalchemy',
        'psycopg2',
        'pymongo',
        'chromadb',
        'pandas',
        'python_dotenv'
    ]
    
    results = {}
    for module in modules:
        results[module] = check_import(module)
    
    print("\n=== Summary ===")
    for module, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {module}")

if __name__ == "__main__":
    main()
