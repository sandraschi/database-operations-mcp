"""
Comprehensive test suite for database operation tools with FastMCP detection.

This script:
1. Tests import capabilities of all tool modules
2. Detects FastMCP registration issues
3. Provides diagnostic information about tool structure
4. Generates detailed reports about compliance issues
"""

import ast
import importlib
import inspect
import json
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List

# Configuration
OUTPUT_DIR = Path("test_reports")
OUTPUT_DIR.mkdir(exist_ok=True)


def setup_python_path():
    """Set up Python path to handle imports properly."""
    project_root = Path(__file__).parent.parent.absolute()
    src_dir = project_root / "src"

    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    print(f"Project root: {project_root}")
    print(f"Source directory: {src_dir}")

    package_dir = src_dir / "database_operations_mcp"
    tools_dir = package_dir / "tools"

    if not package_dir.exists():
        raise FileNotFoundError(f"Package directory not found: {package_dir}")
    if not tools_dir.exists():
        raise FileNotFoundError(f"Tools directory not found: {tools_dir}")

    return package_dir, tools_dir


class ToolTester:
    """Enhanced test runner with FastMCP compliance checking."""

    def __init__(self):
        self.results = {
            "summary": {
                "total_modules": 0,
                "modules_imported": 0,
                "import_failures": 0,
                "syntax_errors": 0,
                "fastmcp_issues": 0,
                "total_functions": 0,
                "mcp_decorated_functions": 0,
            },
            "modules": {},
            "fastmcp_compliance": {"issues": [], "recommendations": []},
        }
        self.package_dir, self.tools_dir = setup_python_path()

    def get_tool_modules(self) -> List[str]:
        """Get list of all tool modules to test."""
        modules = []

        for item in self.tools_dir.iterdir():
            if item.is_file() and item.suffix == ".py":
                if not item.name.startswith("_") and item.name != "__init__.py":
                    modules.append(item.stem)
            elif item.is_dir() and not item.name.startswith("_"):
                subdir_init = item / "__init__.py"
                if subdir_init.exists():
                    modules.append(item.name)

        print(f"Found {len(modules)} tool modules: {', '.join(modules)}")
        return modules

    def analyze_source_code(self, module_name: str, file_path: Path) -> Dict[str, Any]:
        """Analyze source code for FastMCP compliance and syntax issues."""
        analysis = {
            "syntax_valid": False,
            "mcp_decorators": [],
            "function_definitions": [],
            "indentation_issues": [],
            "import_issues": [],
            "fastmcp_compliance": "unknown",
        }

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()

            # Try to parse the AST
            try:
                ast.parse(source)
                analysis["syntax_valid"] = True
            except SyntaxError as e:
                analysis["syntax_error"] = str(e)
                analysis["syntax_line"] = e.lineno
                return analysis

            # Analyze the AST for patterns
            lines = source.split("\n")

            # Look for MCP decorators and function definitions

            for i, line in enumerate(lines, 1):
                stripped = line.strip()

                if stripped.startswith("@mcp.tool"):
                    # Check indentation of MCP decorator
                    line_indent = len(line) - len(line.lstrip())
                    analysis["mcp_decorators"].append(
                        {"line": i, "indentation": line_indent, "text": stripped}
                    )

                    # Check if this decorator is incorrectly indented
                    if line_indent > 0:
                        analysis["indentation_issues"].append(
                            {
                                "line": i,
                                "issue": "MCP decorator should be at module level (no indentation)",
                                "current_indent": line_indent,
                            }
                        )

                if stripped.startswith("def ") or stripped.startswith("async def "):
                    line_indent = len(line) - len(line.lstrip())
                    func_name = (
                        stripped.split("(")[0].replace("def ", "").replace("async ", "").strip()
                    )

                    analysis["function_definitions"].append(
                        {
                            "line": i,
                            "name": func_name,
                            "indentation": line_indent,
                            "is_async": "async" in stripped,
                        }
                    )

                # Check for problematic imports
                if "from ..." in stripped or "from ...." in stripped:
                    analysis["import_issues"].append(
                        {"line": i, "issue": "Relative import may cause issues", "text": stripped}
                    )

            # Determine FastMCP compliance
            if analysis["mcp_decorators"]:
                # Check if any decorators are incorrectly indented
                bad_decorators = [d for d in analysis["mcp_decorators"] if d["indentation"] > 0]
                if bad_decorators:
                    analysis["fastmcp_compliance"] = "non_compliant"
                    analysis["compliance_issues"] = [
                        f"MCP decorators on lines {[d['line'] for d in bad_decorators]} "
                        f"are incorrectly indented"
                    ]
                else:
                    analysis["fastmcp_compliance"] = "compliant"
            else:
                analysis["fastmcp_compliance"] = "no_mcp_tools"

            return analysis

        except Exception as e:
            analysis["analysis_error"] = str(e)
            return analysis

    def test_module_import(self, module_name: str) -> Dict[str, Any]:
        """Test importing a module and analyze its structure."""
        module_path = self.tools_dir / f"{module_name}.py"
        if not module_path.exists():
            # Check if it's a directory
            module_path = self.tools_dir / module_name
            if module_path.is_dir():
                module_path = module_path / "__init__.py"

        result = {
            "module_name": module_name,
            "import_success": False,
            "functions": [],
            "classes": [],
            "errors": [],
            "source_analysis": None,
        }

        # First, analyze the source code
        if module_path.exists():
            result["source_analysis"] = self.analyze_source_code(module_name, module_path)

        # Try to import the module
        try:
            module_full_name = f"database_operations_mcp.tools.{module_name}"
            module = importlib.import_module(module_full_name)
            result["import_success"] = True

            # Analyze imported module
            for name, obj in inspect.getmembers(module):
                if not name.startswith("_"):
                    if inspect.isfunction(obj) or inspect.iscoroutinefunction(obj):
                        func_info = {
                            "name": name,
                            "is_coroutine": inspect.iscoroutinefunction(obj),
                            "module": getattr(obj, "__module__", "unknown"),
                            "signature": str(inspect.signature(obj)) if callable(obj) else None,
                        }

                        # Check if function is defined in this module
                        if func_info["module"] == module_full_name:
                            result["functions"].append(func_info)
                    elif inspect.isclass(obj):
                        result["classes"].append(
                            {"name": name, "module": getattr(obj, "__module__", "unknown")}
                        )

        except Exception as e:
            result["import_error"] = str(e)
            result["import_traceback"] = traceback.format_exc()

        return result

    def run_tests(self):
        """Run comprehensive tests on all modules."""
        modules = self.get_tool_modules()
        self.results["summary"]["total_modules"] = len(modules)

        for module_name in modules:
            print(f"\nTesting module: {module_name}")
            print("-" * 50)

            result = self.test_module_import(module_name)
            self.results["modules"][module_name] = result

            # Update summary statistics
            if result["import_success"]:
                self.results["summary"]["modules_imported"] += 1
            else:
                self.results["summary"]["import_failures"] += 1

            # Check for syntax errors
            if result["source_analysis"]:
                if not result["source_analysis"]["syntax_valid"]:
                    self.results["summary"]["syntax_errors"] += 1

                # Count FastMCP issues
                if result["source_analysis"]["fastmcp_compliance"] == "non_compliant":
                    self.results["summary"]["fastmcp_issues"] += 1

                # Count functions and MCP decorators
                self.results["summary"]["total_functions"] += len(result["functions"])
                self.results["summary"]["mcp_decorated_functions"] += len(
                    result["source_analysis"]["mcp_decorators"]
                )

        # Generate FastMCP compliance analysis
        self.analyze_fastmcp_compliance()

    def analyze_fastmcp_compliance(self):
        """Analyze overall FastMCP compliance."""
        issues = []
        recommendations = []

        for module_name, module_result in self.results["modules"].items():
            if not module_result["source_analysis"]:
                continue

            analysis = module_result["source_analysis"]

            # Check for syntax errors
            if not analysis["syntax_valid"]:
                issues.append(f"{module_name}: Syntax error prevents proper analysis")
                continue

            # Check for indentation issues
            if analysis["indentation_issues"]:
                for issue in analysis["indentation_issues"]:
                    issues.append(f"{module_name} line {issue['line']}: {issue['issue']}")

            # Check for import issues
            if analysis["import_issues"]:
                for issue in analysis["import_issues"]:
                    issues.append(f"{module_name} line {issue['line']}: {issue['issue']}")

            # Check FastMCP compliance
            if analysis["fastmcp_compliance"] == "non_compliant":
                issues.append(f"{module_name}: FastMCP decorator usage is non-compliant")

        # Generate recommendations
        if issues:
            recommendations.extend(
                [
                    "Fix indentation: MCP decorators (@mcp.tool()) should be at "
                    "module level (no indentation)",
                    "Fix function definitions: Functions should be defined at "
                    "module level after decorators",
                    "Fix imports: Use absolute imports instead of relative imports where possible",
                    "Ensure proper FastMCP 2.10.1+ structure",
                    "Test each module individually after fixes",
                ]
            )

        self.results["fastmcp_compliance"] = {"issues": issues, "recommendations": recommendations}

    def generate_report(self):
        """Generate comprehensive test and compliance report."""
        summary = self.results["summary"]

        # Create text report
        report_lines = [
            "=" * 80,
            "DATABASE OPERATIONS MCP - COMPREHENSIVE TEST REPORT",
            "=" * 80,
            f"Total Modules: {summary['total_modules']}",
            f"Successfully Imported: {summary['modules_imported']}",
            f"Import Failures: {summary['import_failures']}",
            f"Syntax Errors: {summary['syntax_errors']}",
            f"FastMCP Issues: {summary['fastmcp_issues']}",
            f"Total Functions: {summary['total_functions']}",
            f"MCP Decorated Functions: {summary['mcp_decorated_functions']}",
            "",
            "FASTMCP COMPLIANCE ANALYSIS:",
            "-" * 40,
        ]

        compliance = self.results["fastmcp_compliance"]
        if compliance["issues"]:
            report_lines.extend([f"Found {len(compliance['issues'])} compliance issues:", ""])
            for issue in compliance["issues"]:
                report_lines.append(f"  ❌ {issue}")

            report_lines.extend(["", "RECOMMENDATIONS:", ""])
            for rec in compliance["recommendations"]:
                report_lines.append(f"  💡 {rec}")
        else:
            report_lines.append("  ✅ No FastMCP compliance issues found!")

        report_lines.extend(["", "MODULE DETAILS:", "-" * 40])

        # Add module details
        for module_name, module_result in self.results["modules"].items():
            report_lines.append(f"\n{module_name.upper()}:")

            if module_result["import_success"]:
                report_lines.append("  ✅ Import: SUCCESS")
                report_lines.append(f"  Functions: {len(module_result['functions'])}")

                for func in module_result["functions"]:
                    func_type = "async" if func["is_coroutine"] else "sync"
                    report_lines.append(f"    - {func['name']} ({func_type})")
            else:
                report_lines.append("  ❌ Import: FAILED")
                if "import_error" in module_result:
                    report_lines.append(f"    Error: {module_result['import_error']}")

            # Add source analysis
            if module_result["source_analysis"]:
                analysis = module_result["source_analysis"]
                if not analysis["syntax_valid"]:
                    report_lines.append("  ❌ Syntax: INVALID")
                    if "syntax_error" in analysis:
                        report_lines.append(f"    Error: {analysis['syntax_error']}")
                else:
                    report_lines.append("  ✅ Syntax: VALID")

                if analysis["mcp_decorators"]:
                    report_lines.append(f"  MCP Decorators: {len(analysis['mcp_decorators'])}")

                if analysis["indentation_issues"]:
                    report_lines.append(
                        f"  ❌ Indentation Issues: {len(analysis['indentation_issues'])}"
                    )

        # Save reports
        report_path = OUTPUT_DIR / "comprehensive_test_report.txt"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))

        json_path = OUTPUT_DIR / "comprehensive_test_results.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2)

        print("\nReports saved:")
        print(f"  Text report: {report_path}")
        print(f"  JSON data: {json_path}")

        return report_path, json_path


def main():
    """Main function to run comprehensive tests."""
    print("Database Operations MCP - Comprehensive Test Suite")
    print("=" * 60)
    print("Testing import capabilities and FastMCP compliance...")
    print()

    try:
        tester = ToolTester()
        tester.run_tests()
        report_path, json_path = tester.generate_report()

        # Print summary
        summary = tester.results["summary"]
        compliance = tester.results["fastmcp_compliance"]

        print("\n" + "=" * 60)
        print("SUMMARY:")
        print(f"  Modules tested: {summary['total_modules']}")
        print(f"  Import success: {summary['modules_imported']}")
        print(f"  Import failures: {summary['import_failures']}")
        print(f"  Syntax errors: {summary['syntax_errors']}")
        print(f"  FastMCP issues: {summary['fastmcp_issues']}")
        print(f"  Total functions: {summary['total_functions']}")

        if compliance["issues"]:
            print(f"\n❌ Found {len(compliance['issues'])} compliance issues")
            print("   See report for details and recommendations")
            return 1
        else:
            print("\n✅ No major compliance issues found")
            return 0

    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
