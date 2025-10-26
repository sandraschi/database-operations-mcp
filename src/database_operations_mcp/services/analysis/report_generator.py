"""
Database report generation service.

This module provides functionality to generate comprehensive human-readable
database analysis reports.
"""

from datetime import datetime
from pathlib import Path

from database_operations_mcp.services.analysis.content_analyzer import (
    ContentAnalyzer,
)
from database_operations_mcp.services.analysis.error_detector import ErrorDetector
from database_operations_mcp.services.analysis.health_checker import HealthChecker
from database_operations_mcp.services.analysis.structure_analyzer import (
    StructureAnalyzer,
)


class ReportGenerator:
    """Generate comprehensive database analysis reports.

    Provides functionality to generate human-readable reports summarizing
    database structure, content, health, and recommendations.
    """

    def __init__(self):
        """Initialize report generator."""
        self.structure_analyzer = StructureAnalyzer()
        self.content_analyzer = ContentAnalyzer()
        self.error_detector = ErrorDetector()
        self.health_checker = HealthChecker()

    async def generate_report(self, db_path: str, include_samples: bool = True) -> str:
        """Generate comprehensive text report.

        Creates a human-readable report covering all aspects of database analysis.

        Args:
            db_path: Path to database file
            include_samples: Whether to include data samples

        Returns:
            Markdown-formatted report string
        """
        # Gather all information
        db_info = await self.structure_analyzer.get_database_info(db_path)
        schema = await self.structure_analyzer.analyze_schema(db_path)
        health = await self.health_checker.check_health(db_path)
        content_sample = (
            await self.content_analyzer.sample_content(db_path, schema["tables"][0]["name"])
            if schema["tables"] and include_samples
            else None
        )

        # Build report
        report = []
        report.append("# Database Analysis Report\n")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"**Database:** {Path(db_path).name}\n")
        report.append(f"**Type:** {db_info['database_type']}\n")
        report.append(f"**File Size:** {db_info.get('file_size', 0) / 1024 / 1024:.2f} MB\n\n")

        # Health Summary
        report.append("## Health Summary\n")
        report.append(
            f"**Overall Score:** {health['overall_score']}/100 ({health['health_status']})\n"
        )
        report.append(f"- Integrity: {health['integrity_score']}/100\n")
        report.append(f"- Corruption: {health['corruption_score']}/100\n")
        report.append(f"- Logical: {health['logical_score']}/100\n")
        report.append(f"- Performance: {health['performance_score']}/100\n\n")

        # Issues
        if health["total_issues"] > 0:
            report.append("### Issues Found\n")
            for issue in health["issues"]:
                report.append(
                    f"- **{issue['severity'].upper()}** ({issue['type']}): {issue['message']}\n"
                )

        # Recommendations
        if health["recommendations"]:
            report.append("\n### Recommendations\n")
            for rec in health["recommendations"]:
                report.append(f"- {rec}\n")

        # Structure
        report.append("\n## Database Structure\n")
        report.append(f"**Tables:** {schema['summary']['table_count']}\n")
        report.append(f"**Views:** {schema['summary']['view_count']}\n")
        report.append(f"**Triggers:** {schema['summary']['trigger_count']}\n\n")

        # Table Details
        report.append("### Tables\n")
        for table in schema["tables"]:
            report.append(f"#### {table['name']}\n")
            report.append(f"- Rows: {table['row_count']:,}\n")
            report.append(f"- Size: {table.get('size_bytes', 0) / 1024:.2f} KB\n")
            report.append(f"- Columns: {len(table['columns'])}\n")
            report.append(f"- Indexes: {len(table['indexes'])}\n")
            report.append(f"- Foreign Keys: {len(table['foreign_keys'])}\n\n")

            if table["columns"]:
                report.append("**Columns:**\n")
                for col in table["columns"]:
                    nullable = "NULL" if not col["not_null"] else "NOT NULL"
                    pk = "PRIMARY KEY" if col["primary_key"] else ""
                    report.append(f"- `{col['name']}` ({col['type']}) {nullable} {pk}\n")
                report.append("\n")

        # Content Sample
        if content_sample:
            report.append("## Content Sample\n")
            report.append(f"### {content_sample['table_name']}\n")
            report.append(f"Total Rows: {content_sample['row_count']:,}\n\n")

            if content_sample["sample_rows"]:
                report.append("**Sample Rows:**\n")
                report.append("```\n")
                for i, row in enumerate(content_sample["sample_rows"][:3], 1):
                    report.append(f"Row {i}:\n")
                    for key, value in row.items():
                        report.append(f"  {key}: {value}\n")
                report.append("```\n")

        return "\n".join(report)
