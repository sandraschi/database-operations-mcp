#!/usr/bin/env python3
"""Test script to check Python environment and imports."""
import sys
import os
import platform
import subprocess

def get_python_info():
    """Get Python environment information."""
    return {
        "executable": sys.executable,
        "version": platform.python_version(),
        "path": sys.path,
        "cwd": os.getcwd(),
        "env": {k: v for k, v in os.environ.items() if k.startswith(('PYTHON', 'PATH', 'VIRTUAL_ENV'))}
    }

def check_package(package_name):
    """Check if a package is importable."""
    try:
        __import__(package_name)
        return True, f"{package_name} imported successfully"
    except ImportError as e:
        return False, f"Failed to import {package_name}: {e}"
    except Exception as e:
        return False, f"Error importing {package_name}: {e}"

def main():
    """Main function to test the environment."""
    print("\n=== Python Environment ===")
    info = get_python_info()
    print(f"Python executable: {info['executable']}")
    print(f"Python version: {info['version']}")
    print("\n=== Environment Variables ===")
    for k, v in info['env'].items():
        print(f"{k}: {v}")
    
    print("\n=== Package Check ===")
    packages = ['fastmcp', 'sqlite3', 'psycopg2', 'pymongo', 'chromadb']
    for pkg in packages:
        success, msg = check_package(pkg)
        status = "✓" if success else "✗"
        print(f"{status} {msg}")
    
    print("\n=== Python Path ===")
    for path in info['path']:
        print(f"- {path}")

if __name__ == "__main__":
    main()
