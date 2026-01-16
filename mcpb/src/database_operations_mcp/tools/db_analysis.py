"""
Database analysis and diagnostics portmanteau tool.

This module provides comprehensive database analysis capabilities through a
single unified interface. Supports structure discovery, content analysis,
error detection, health checking, and report generation.
"""

from typing import Any, Optional, Union

from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.services.analysis import (
    ContentAnalyzer,
    ErrorDetector,
    HealthChecker,
    ReportGenerator,
    StructureAnalyzer,
)

# Initialize analyzers (temporarily disabled for debugging)
# _structure_analyzer = StructureAnalyzer()
# _content_analyzer = ContentAnalyzer()
# _error_detector = ErrorDetector()
# _health_checker = HealthChecker()
# _report_generator = ReportGenerator()


@mcp.tool()
async def db_analysis(db_file_path: str, operation: str = "analyze"):
    """Database analysis tool."""
    if operation == "analyze":
        return {"success": True, "db_file_path": db_file_path, "operation": operation}
    else:
        return {"success": False, "error": f"Unknown operation: {operation}"}


# async def _db_analysis_impl(
    db_file_path: str,
    operation: str,
    analysis_depth: str,
    include_sample_data: bool,
    detect_errors: bool,
    suggest_fixes: bool,
    table_name: Optional[str],
    limit: int,
) -> dict:
    """Database analysis and diagnostics portmanteau tool.

    Comprehensive database analysis consolidating ALL analysis operations into
    a single interface. Examines database files to understand structure, contents,
    health, and potential issues. Supports SQLite, PostgreSQL dumps, MySQL dumps,
    and more with structure discovery, content analysis, error detection, health
    scoring, and actionable recommendations.

    Prerequisites:
        - Database file must exist and be accessible (read permissions)
        - For SQLite databases: Database must be closed (not locked by another process)
        - For error detection: Database file must be readable and valid format
        - For comprehensive analysis: Sufficient system resources for full scan

    Operations:
        - analyze: Complete analysis (structure + content + health)
        - structure: Analyze database structure only
        - content: Analyze database contents and patterns
        - health: Check database health and score
        - errors: Detect errors and issues
        - report: Generate human-readable report
        - suggest_fixes: Generate SQL fix suggestions

    Parameters:
        db_file_path (str, REQUIRED): Path to database file to analyze
            Format: Absolute or relative file path
            Validation: File must exist and be readable
            Supported formats: SQLite (.db, .sqlite), PostgreSQL dumps, MySQL dumps
            Example: 'C:/data/database.db', './database.sqlite', '/var/lib/db.sqlite'

        operation (str, OPTIONAL): Analysis operation to perform
            Valid values: 'analyze', 'structure', 'content', 'health', 'errors',
                         'report', 'suggest_fixes'
            Default: 'analyze'
            Example: 'health', 'errors', 'structure'

        analysis_depth (str, OPTIONAL): Level of analysis to perform
            Valid values: 'quick', 'standard', 'comprehensive'
            Default: 'comprehensive'
            'quick': Basic structure only (fast, ~1 second)
            'standard': Structure + sample data + basic checks (~5 seconds)
            'comprehensive': Full analysis with error detection (~15 seconds)
            Used for: analyze, structure, content operations
            Example: 'quick', 'standard', 'comprehensive'

        include_sample_data (bool, OPTIONAL): Include sample rows from tables
            Default: True
            Behavior: Adds data samples to analysis results for understanding contents
            Used for: analyze, content operations
            Impact: May increase analysis time for large tables
            Example: True, False

        detect_errors (bool, OPTIONAL): Scan for errors and inconsistencies
            Default: True
            Behavior: Includes integrity checks, corruption detection, logical errors
            Used for: analyze, errors operations
            Impact: Adds time but provides valuable diagnostics
            Example: True, False

        suggest_fixes (bool, OPTIONAL): Suggest SQL fixes for detected issues
            Default: True
            Behavior: Generates SQL statements ready to execute to fix errors
            Used for: errors, suggest_fixes operations
            Condition: Only relevant when errors are detected
            Example: True, False

        table_name (str, OPTIONAL): Specific table to analyze
            Format: Valid table name in database
            Required for: content, structure operations (when focusing on single table)
            Behavior: If provided, focuses analysis on single table only
            Example: 'users', 'orders', 'products'

        limit (int, OPTIONAL): Maximum number of sample rows to include
            Format: Positive integer
            Range: 1-100
            Default: 10
            Used for: analyze, content operations (when include_sample_data=True)
            Behavior: Controls how many sample rows per table included in results
            Impact: Higher values increase analysis time and result size
            Example: 5, 10, 20

    Returns:
        Dictionary containing comprehensive analysis results:
            {
                'database_type': str,
                'file_path': str,
                'file_size': int,
                'structure': {
                    'tables': [...],
                    'views': [...],
                    'triggers': [...],
                    'summary': {...}
                },
                'content': {
                    'patterns': {...},
                    'distributions': {...},
                    'samples': {...}
                },
                'health': {
                    'overall_score': float,
                    'integrity_score': float,
                    'corruption_score': float,
                    'issues': [...],
                    'recommendations': [...]
                },
                'errors': [...],
                'suggested_fixes': [...],
                'export_format': 'sqlite'
            }

    Usage:
        Essential starting point for database analysis. Provides comprehensive
        insights into database structure, contents, and health in a single call.
        Supports multiple database types and provides actionable recommendations.

        Common scenarios:
        - Quick health check: db_analysis(
                db_file_path='database.db',
                operation='health',
                analysis_depth='quick'
            )
        - Full analysis: db_analysis(
                db_file_path='database.db',
                operation='analyze',
                analysis_depth='comprehensive'
            )
        - Structure only: db_analysis(
                db_file_path='database.db',
                operation='structure'
            )

    Examples:
        Quick health check:
            result = await db_analysis(
                db_file_path='my_database.db',
                operation='health',
                analysis_depth='quick'
            )
            # Returns health score, issues, recommendations

        Full comprehensive analysis:
            result = await db_analysis(
                db_file_path='production.db',
                operation='analyze',
                analysis_depth='comprehensive',
                include_sample_data=True,
                detect_errors=True,
                suggest_fixes=True
            )
            # Returns complete analysis with structure, content, health

        Detect and fix errors:
            result = await db_analysis(
                db_file_path='corrupted.db',
                operation='errors',
                suggest_fixes=True
            )
            # Returns detected errors with SQL fix suggestions

    Errors:
        Common errors and solutions:
        - 'Database file not found: {path}':
            Cause: File path doesn't exist or is inaccessible
            Fix: Verify file path is correct, check file permissions, ensure file exists
            Workaround: Use absolute paths, check current working directory

        - 'Database file is locked':
            Cause: Another process is using the database file (SQLite)
            Fix: Close all applications using the database, stop database services
            Workaround: Wait for lock to release, copy database file for analysis

        - 'Invalid database format':
            Cause: File is not a recognized database format or is corrupted
            Fix: Verify file is valid database, check file extension, restore from backup
            Workaround: Try different database type, check file headers

        - 'Analysis operation failed: {error}':
            Cause: Internal analysis error or database-specific issue
            Fix: Check database integrity, verify database is not corrupted
            Workaround: Try analysis_depth='quick' first, analyze individual tables

        - 'Table not found: {table_name}':
            Cause: Specified table doesn't exist in database
            Fix: Use db_schema(operation='list_tables') to see available tables
            Workaround: Omit table_name to analyze all tables

    See Also:
        - db_operations: Database query and manipulation operations
        - db_schema: Database schema management
        - db_management: Database administration operations
    """
    return await _db_analysis_impl(
        db_file_path, operation, analysis_depth, include_sample_data,
        detect_errors, suggest_fixes, table_name, limit
    )


async def _db_analysis_impl(
    db_file_path: str,
    operation: str,
    analysis_depth: str,
    include_sample_data: bool,
    detect_errors: bool,
    suggest_fixes: bool,
    table_name: str,
    limit: int,
):
    """Internal implementation of database analysis."""
    print(f"DEBUG: _db_analysis_impl called with db_file_path={db_file_path}")
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
        report = await _report_generator.generate_report(
            db_file_path, include_samples=include_sample_data
        )
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
        content = await _content_analyzer.sample_content(
            db_file_path, structure["tables"][0]["name"], limit=limit
        )
        result["sample_data"] = content

    if detect_errors:
        errors = await _error_detector.find_logical_errors(db_file_path)
        result["errors"] = errors

        if suggest_fixes:
            fixes = await _error_detector.suggest_fixes(db_file_path)
            result["suggested_fixes"] = fixes

    return result
