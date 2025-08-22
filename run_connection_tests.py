"""
Simple script to run connection tools tests with detailed output.
"""
import sys
import pytest

def main():
    """Run the connection tools tests with detailed output."""
    print("Running connection tools tests...")
    
    # Run pytest programmatically
    exit_code = pytest.main([
        "tests/unit/test_connection_tools.py",
        "-v",
        "--tb=short"  # Shorter traceback for better readability
    ])
    
    print(f"\nTests completed with exit code: {exit_code}")
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
