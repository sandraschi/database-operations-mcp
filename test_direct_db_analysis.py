#!/usr/bin/env python3
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Import services directly, not through MCP
from database_operations_mcp.services.analysis.structure_analyzer import StructureAnalyzer
from database_operations_mcp.services.analysis.content_analyzer import ContentAnalyzer
from database_operations_mcp.services.analysis.error_detector import ErrorDetector
from database_operations_mcp.services.analysis.health_checker import HealthChecker

# Initialize analyzers
_structure_analyzer = StructureAnalyzer()
_content_analyzer = ContentAnalyzer()
_error_detector = ErrorDetector()
_health_checker = HealthChecker()

async def db_analysis_direct(
    db_file_path: str,
    operation: str = "analyze",
    analysis_depth: str = "comprehensive",
    include_sample_data: bool = True,
    detect_errors: bool = True,
    suggest_fixes: bool = True,
    table_name=None,
    limit: int = 10,
):
    """Direct version of db_analysis without MCP wrapper."""
    # Route to appropriate analysis handler
    if operation == "structure" or operation == "analyze":
        structure = await _structure_analyzer.analyze_schema(db_file_path)
        db_info = await _structure_analyzer.get_database_info(db_file_path)

        if operation == "structure":
            return {
                "success": True,
                "operation": operation,
                "database_type": db_info["database_type"],
                "file_path": db_file_path,
                "file_size": db_info.get("file_size", 0),
                "structure": structure,
            }

    if operation == "content":
        # Get structure first
        structure = await _structure_analyzer.analyze_schema(db_file_path)

        if table_name:
            content = await _content_analyzer.sample_content(db_file_path, table_name, limit=limit)
            patterns = await _content_analyzer.detect_patterns(db_file_path, table_name)
            distributions = await _content_analyzer.analyze_distributions(db_file_path, table_name)
        else:
            content = await _content_analyzer.sample_content(
                db_file_path,
                structure["tables"][0]["name"] if structure["tables"] else "",
                limit=limit,
            )
            patterns = {}
            distributions = {}

        return {
            "success": True,
            "operation": operation,
            "database_type": structure["database_type"],
            "content": {
                "patterns": patterns,
                "distributions": distributions,
                "samples": content,
            },
        }

    if operation == "health":
        health = await _health_checker.check_health(db_file_path)
        return {
            "success": True,
            "operation": operation,
            "health": health,
        }

    if operation == "errors":
        integrity = await _error_detector.check_integrity(db_file_path)
        corruption = await _error_detector.detect_corruption(db_file_path)
        logical_errors = await _error_detector.find_logical_errors(db_file_path)

        result = {
            "success": True,
            "operation": operation,
            "integrity": integrity,
            "corruption": corruption,
            "logical_errors": logical_errors,
        }

        if suggest_fixes:
            fixes = await _error_detector.suggest_fixes(db_file_path)
            result["suggested_fixes"] = fixes

        return result

    if operation == "report":
        # This would need ReportGenerator, skipping for now
        return {"success": False, "error": "Report operation not implemented in direct test"}

    # Default: full comprehensive analysis
    structure = await _structure_analyzer.analyze_schema(db_file_path)
    db_info = await _structure_analyzer.get_database_info(db_file_path)
    health = await _health_checker.check_health(db_file_path)

    result = {
        "success": True,
        "operation": "analyze",
        "database_type": db_info["database_type"],
        "file_path": db_file_path,
        "file_size": db_info.get("file_size", 0),
        "structure": structure,
        "health": health,
    }

    return result

async def test_direct():
    db_path = r"L:\Multimedia Files\Written Word\metadata.db"

    try:
        print(f"Testing direct db_analysis on: {db_path}")
        result = await db_analysis_direct(
            db_file_path=db_path,
            operation="analyze",
            analysis_depth="quick",
            include_sample_data=False,
            detect_errors=False,
            suggest_fixes=False
        )
        print("Direct analysis successful!")
        print(f"Database type: {result.get('database_type')}")
        print(f"Tables found: {len(result.get('structure', {}).get('tables', []))}")
        return True
    except Exception as e:
        print(f"Direct analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_direct())
    print(f"Test {'PASSED' if success else 'FAILED'}")
