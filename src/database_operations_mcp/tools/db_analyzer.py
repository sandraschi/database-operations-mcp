from typing import Any

from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.operation_types import DbAnalyzerOperation
from database_operations_mcp.services.analysis import (
    ContentAnalyzer,
    ErrorDetector,
    HealthChecker,
    ReportGenerator,
    StructureAnalyzer,
)
from database_operations_mcp.tool_responses import unknown_operation_response
from database_operations_mcp.tools.help_tools import HelpSystem

# Initialize analyzers
_structure_analyzer = StructureAnalyzer()
_content_analyzer = ContentAnalyzer()
_error_detector = ErrorDetector()
_health_checker = HealthChecker()
_report_generator = ReportGenerator()


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def db_analyzer(
    db_file_path: str,
    operation: DbAnalyzerOperation = "analyze",
    analysis_depth: str = "comprehensive",
    include_sample_data: bool = True,
    detect_errors: bool = True,
    suggest_fixes: bool = True,
    table_name: str | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """Database analysis and diagnostics portmanteau tool.

    Operations: analyze, structure, content, health, errors, report, suggest_fixes.
    analysis_depth: quick | standard | comprehensive (default: comprehensive)
    db_file_path: path to SQLite/PostgreSQL/MySQL dump file (required)

    Returns:
        On success: dict with success=True, operation, and operation-specific keys
        (structure, health, report, content, errors, suggested_fixes, etc.).

    Errors:
        Unknown operation returns error_type=invalid_input with available_operations.
        File access failures: user_fixable — verify db_file_path exists and is readable.
    """
    _known: set[str] = {"structure", "analyze", "content", "health", "errors", "report"}
    if operation not in _known:
        return unknown_operation_response(operation, sorted(_known))

    limit = max(1, min(limit, 10_000))

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
        tables_to_analyze = []

        if table_name:
            tables_to_analyze = [table_name]
        else:
            # Analyze top 5 tables if none specified
            tables_to_analyze = [t["name"] for t in structure["tables"][:5]]

        results_by_table = {}
        for t in tables_to_analyze:
            content = await _content_analyzer.sample_content(db_file_path, t, limit=limit)
            patterns = await _content_analyzer.detect_patterns(db_file_path, t)
            distributions = await _content_analyzer.analyze_distributions(db_file_path, t)
            results_by_table[t] = {
                "patterns": patterns,
                "distributions": distributions,
                "samples": content,
            }

        return {
            "success": True,
            "operation": operation,
            "database_type": structure["database_type"],
            "tables_analyzed": tables_to_analyze,
            "content": results_by_table,
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
        report = await _report_generator.generate_report(db_file_path, include_samples=include_sample_data)
        return {
            "success": True,
            "operation": operation,
            "report": report,
        }

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

    if include_sample_data and structure["tables"]:
        tables_to_sample = [t["name"] for t in structure["tables"][:5]]
        samples_by_table = {}
        for t in tables_to_sample:
            content = await _content_analyzer.sample_content(db_file_path, t, limit=limit)
            samples_by_table[t] = {
                "samples": content,
                "patterns": {},
                "distributions": {},
            }
        result["content"] = samples_by_table
        result["tables_sampled"] = tables_to_sample

    if detect_errors:
        errors = await _error_detector.find_logical_errors(db_file_path)
        result["errors"] = errors

        if suggest_fixes:
            fixes = await _error_detector.suggest_fixes(db_file_path)
            result["suggested_fixes"] = fixes

    return result
