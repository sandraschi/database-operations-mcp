"""
Database analysis and diagnostics portmanteau tool.

This module provides comprehensive database analysis capabilities through a
single unified interface. Supports structure discovery, content analysis,
error detection, health checking, and report generation.
"""

from typing import Any, Dict, Optional

from mcp import mcp

from database_operations_mcp.services.analysis import (
    ContentAnalyzer,
    ErrorDetector,
    HealthChecker,
    ReportGenerator,
    StructureAnalyzer,
)

# Initialize analyzers
_structure_analyzer = StructureAnalyzer()
_content_analyzer = ContentAnalyzer()
_error_detector = ErrorDetector()
_health_checker = HealthChecker()
_report_generator = ReportGenerator()


@mcp.tool()
async def db_analysis(
    db_file_path: str,
    operation: str = "analyze",
    analysis_depth: str = "comprehensive",
    include_sample_data: bool = True,
    detect_errors: bool = True,
    suggest_fixes: bool = True,
    table_name: Optional[str] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    """Comprehensive database analysis and diagnostics.

    Examines a database file to understand its structure, contents, health,
    and potential issues. Can analyze SQLite, PostgreSQL dumps, MySQL dumps,
    and more. Provides structure discovery, content analysis, error detection,
    health scoring, and actionable recommendations.

    Parameters:
        db_file_path: Path to database file to analyze
            - Must be valid file path
            - Supports SQLite (.db, .sqlite), PostgreSQL dumps, MySQL dumps
            - File must exist and be accessible
        operation: Analysis operation to perform
            - 'analyze': Complete analysis (structure + content + health)
            - 'structure': Analyze database structure only
            - 'content': Analyze database contents and patterns
            - 'health': Check database health and score
            - 'errors': Detect errors and issues
            - 'report': Generate human-readable report
            - 'suggest_fixes': Generate SQL fix suggestions
        analysis_depth: Level of analysis to perform
            - 'quick': Basic structure only (fast, ~1 second)
            - 'standard': Structure + sample data + basic checks (~5 seconds)
            - 'comprehensive': Full analysis with error detection (~15 seconds)
        include_sample_data: Whether to include sample rows from tables
            - Adds data samples to analysis results
            - Useful for understanding actual contents
            - May increase analysis time
        detect_errors: Whether to scan for errors and inconsistencies
            - Includes integrity checks, corruption detection
            - Identifies logical errors and data quality issues
            - Adds time to analysis but provides valuable diagnostics
        suggest_fixes: Whether to suggest SQL fixes for detected issues
            - Generates SQL statements to fix detected errors
            - Provides actionable solutions
            - Only relevant when errors detected
        table_name: Specific table to analyze (optional)
            - If provided, focuses analysis on single table
            - Omit to analyze entire database
            - Used with 'content' and 'structure' operations
        limit: Maximum number of sample rows to include
            - Controls how many sample rows per table
            - Range: 1-100
            - Higher values increase analysis time

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

    Notes:
        - Database file must be accessible and not locked
        - SQLite databases must be closed before analysis
        - Large databases may take longer to analyze
        - Comprehensive analysis includes all checks and may be slow
        - Sample data helps understand actual database contents
        - Error detection can identify corruption and logical issues
        - Suggested fixes are SQL statements ready to execute

    See Also:
        - db_operations: Database query and manipulation operations
        - db_schema: Database schema management
        - db_management: Database administration operations
    """
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
            content = await _content_analyzer.sample_content(
                db_file_path, table_name, limit=limit
            )
            patterns = await _content_analyzer.detect_patterns(db_file_path, table_name)
            distributions = await _content_analyzer.analyze_distributions(
                db_file_path, table_name
            )
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

