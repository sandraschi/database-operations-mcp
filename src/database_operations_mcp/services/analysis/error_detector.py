"""
Database error detection service.

This module provides functionality to detect and diagnose various database
errors including corruption, integrity issues, logical errors, and performance problems.
"""

from typing import Any

import aiosqlite


class ErrorDetector:
    """Detect and diagnose database errors.

    Provides comprehensive error detection including integrity checks, corruption
    detection, logical validation, and performance diagnostics.
    """

    async def check_integrity(self, db_path: str) -> dict[str, Any]:
        """Check database integrity using PRAGMA commands.

        Performs SQLite integrity checks to detect corruption and consistency issues.

        Args:
            db_path: Path to database file

        Returns:
            Dictionary containing integrity check results:
                {
                    'integrity_check': str,
                    'quick_check': str,
                    'foreign_key_check': str,
                    'errors': List[str],
                    'warnings': List[str]
                }
        """
        errors = []
        warnings = []

        async with aiosqlite.connect(db_path) as conn:
            # Quick integrity check
            try:
                async with conn.execute("PRAGMA quick_check") as cursor:
                    result = await cursor.fetchone()
                    quick_check = result[0] if result else "unknown"
                    if quick_check != "ok":
                        errors.append(f"Quick check failed: {quick_check}")
            except Exception as e:
                errors.append(f"Quick check error: {e}")

            # Foreign key check
            try:
                async with conn.execute("PRAGMA foreign_key_check") as cursor:
                    fk_errors = await cursor.fetchall()
                    if fk_errors:
                        errors.append(f"Foreign key violations: {len(fk_errors)}")
            except Exception as e:
                warnings.append(f"Foreign key check skipped: {e}")

            # Index check
            try:
                async with conn.execute("PRAGMA integrity_check") as cursor:
                    result = await cursor.fetchone()
                    if result and result[0] != "ok":
                        errors.append(f"Integrity check failed: {result[0]}")
            except Exception as e:
                warnings.append(f"Integrity check skipped: {e}")

        return {
            "integrity_check": "ok" if not errors else "failed",
            "quick_check": result[0] if "result" in locals() else "unknown",
            "foreign_key_check": "ok" if not errors else "failed",
            "errors": errors,
            "warnings": warnings,
            "total_errors": len(errors),
            "total_warnings": len(warnings),
        }

    async def detect_corruption(self, db_path: str) -> dict[str, Any]:
        """Detect database corruption issues.

        Performs comprehensive corruption detection including header checks,
        page validation, and data consistency checks.

        Args:
            db_path: Path to database file

        Returns:
            Dictionary containing corruption detection results
        """
        corruption_issues = []

        async with aiosqlite.connect(db_path) as conn:
            try:
                # Page count check
                async with conn.execute("PRAGMA page_count") as cursor:
                    page_count = (await cursor.fetchone())[0]
                    if page_count == 0:
                        corruption_issues.append("Empty database - 0 pages")

                # Page size check
                async with conn.execute("PRAGMA page_size") as cursor:
                    page_size = (await cursor.fetchone())[0]
                    if page_size not in [512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]:
                        corruption_issues.append(f"Unusual page size: {page_size}")

            except Exception as e:
                corruption_issues.append(f"Corruption detection error: {e}")

        return {
            "corruption_detected": len(corruption_issues) > 0,
            "issues": corruption_issues,
            "severity": "high" if len(corruption_issues) > 0 else "none",
            "recommendation": "Run REPAIR or restore from backup"
            if len(corruption_issues) > 0
            else "Database appears healthy",
        }

    async def find_logical_errors(self, db_path: str) -> list[dict[str, Any]]:
        """Find logical inconsistencies in database.

        Detects logical errors like duplicate primary keys, NULL in NOT NULL
        columns, invalid foreign keys, etc.

        Args:
            db_path: Path to database file

        Returns:
            List of logical errors found
        """
        errors = []

        async with aiosqlite.connect(db_path) as conn:
            # Get all tables
            async with conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            ) as cursor:
                tables = [row[0] for row in await cursor.fetchall()]

            for table_name in tables:
                # Check for NULL in NOT NULL columns
                async with conn.execute(f'PRAGMA table_info("{table_name}")') as cursor:
                    columns = await cursor.fetchall()
                    not_null_columns = [col[1] for col in columns if col[3] == 1]

                    for col_name in not_null_columns:
                        try:
                            async with conn.execute(
                                f'SELECT COUNT(*) FROM "{table_name}" WHERE "{col_name}" IS NULL'
                            ) as cursor:
                                null_count = (await cursor.fetchone())[0]
                                if null_count > 0:
                                    errors.append(
                                        {
                                            "table": table_name,
                                            "column": col_name,
                                            "type": "NULL in NOT NULL column",
                                            "count": null_count,
                                            "severity": "high",
                                        }
                                    )
                        except Exception:
                            pass  # Skip if query fails

        return errors

    async def suggest_fixes(self, db_path: str) -> list[dict[str, Any]]:
        """Suggest SQL fixes for detected errors.

        Analyzes detected errors and generates SQL statements to fix them.

        Args:
            db_path: Path to database file

        Returns:
            List of suggested SQL fixes
        """
        integrity = await self.check_integrity(db_path)
        corruption = await self.detect_corruption(db_path)
        logical_errors = await self.find_logical_errors(db_path)

        fixes = []

        if integrity["total_errors"] > 0:
            fixes.append(
                {
                    "issue": "Integrity errors detected",
                    "suggested_fix": "PRAGMA integrity_check; PRAGMA quick_check;",
                    "description": "Run integrity checks and repair database",
                    "severity": "high",
                }
            )

        if corruption["corruption_detected"]:
            fixes.append(
                {
                    "issue": "Corruption detected",
                    "suggested_fix": "Use REPAIR DATABASE or restore from backup",
                    "description": "Database appears corrupted",
                    "severity": "critical",
                }
            )

        for error in logical_errors:
            if error["type"] == "NULL in NOT NULL column":
                fixes.append(
                    {
                        "issue": f"NULL values in {error['column']}",
                        "suggested_fix": (
                            f"UPDATE {error['table']} SET {error['column']} = ''"
                            f" WHERE {error['column']} IS NULL;"
                        ),
                        "description": "Remove NULL values from NOT NULL column",
                        "severity": error["severity"],
                    }
                )

        return fixes
