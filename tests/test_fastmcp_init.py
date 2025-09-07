"""Test FastMCP initialization and basic functionality."""
import sys
import json
from pathlib import Path

def run_tests():
    """Run FastMCP initialization tests and return results."""
    results = {
        "tests_run": 0,
        "tests_passed": 0,
        "details": {}
    }
    
    # Test 1: Basic initialization
    test_name = "basic_initialization"
    results["tests_run"] += 1
    try:
        from fastmcp import FastMCP
        mcp = FastMCP()
        results["details"][test_name] = {
            "status": "PASS",
            "name": getattr(mcp, "name", "Not set"),
            "type": type(mcp).__name__
        }
        results["tests_passed"] += 1
    except Exception as e:
        results["details"][test_name] = {
            "status": "FAIL",
            "error": str(e),
            "type": type(e).__name__
        }
    
    # Test 2: Initialization with name and version
    test_name = "initialization_with_params"
    results["tests_run"] += 1
    try:
        from fastmcp import FastMCP
        mcp = FastMCP(name="test-mcp", version="1.0.0")
        results["details"][test_name] = {
            "status": "PASS",
            "name": getattr(mcp, "name", "Not set"),
            "version": getattr(mcp, "version", "Not set")
        }
        results["tests_passed"] += 1
    except Exception as e:
        results["details"][test_name] = {
            "status": "FAIL",
            "error": str(e),
            "type": type(e).__name__
        }
    
    # Test 3: Check available methods
    test_name = "check_available_methods"
    results["tests_run"] += 1
    try:
        from fastmcp import FastMCP
        mcp = FastMCP()
        methods = [m for m in dir(mcp) if not m.startswith('_')]
        results["details"][test_name] = {
            "status": "PASS",
            "method_count": len(methods),
            "sample_methods": methods[:5]  # Show first 5 methods
        }
        results["tests_passed"] += 1
    except Exception as e:
        results["details"][test_name] = {
            "status": "FAIL",
            "error": str(e),
            "type": type(e).__name__
        }
    
    return results

if __name__ == "__main__":
    # Run tests and get results
    test_results = run_tests()
    
    # Write results to JSON file
    output_file = Path("test_results.json")
    with open(output_file, "w") as f:
        json.dump(test_results, f, indent=2)
    
    # Print summary
    print(f"Tests run: {test_results['tests_run']}")
    print(f"Tests passed: {test_results['tests_passed']}")
    print(f"Tests failed: {test_results['tests_run'] - test_results['tests_passed']}")
    print(f"Detailed results saved to: {output_file}")
