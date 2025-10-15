"""
Test runner for database operations tools.
This script runs tests while respecting the package structure and relative imports.
"""

import sys
from pathlib import Path


def run_tests():
    # Set up the Python path
    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src"

    # Add necessary paths to Python path
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(src_dir))

    # Import the test module after setting up the path
    from tests.test_all_tools import ToolTester

    # Create and run the test suite
    tester = ToolTester()
    tester.run_tests()

    # Generate the test report
    tester.generate_report()

    # Print a summary
    print("\nTest execution completed.")
    print(f"Results saved to: {tester.results_file}")


if __name__ == "__main__":
    run_tests()
