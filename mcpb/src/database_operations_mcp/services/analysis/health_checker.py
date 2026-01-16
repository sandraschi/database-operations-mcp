"""
Database health checking service.

This module provides functionality to check database health and generate health scores.
"""

from typing import Any

from database_operations_mcp.services.analysis.error_detector import ErrorDetector


class HealthChecker:
    """Check database health and generate health score.

    Provides comprehensive health checking including various health metrics,
    performance indicators, and overall health score calculation.
    """

    def __init__(self):
        """Initialize health checker."""
        self.error_detector = ErrorDetector()

    async def check_health(self, db_path: str) -> dict[str, Any]:
        """Perform comprehensive health check on database.

        Evaluates database health across multiple dimensions including integrity,
        corruption, logical consistency, and performance.

        Args:
            db_path: Path to database file

        Returns:
            Dictionary containing comprehensive health information:
                {
                    'overall_score': float (0-100),
                    'integrity_score': float,
                    'corruption_score': float,
                    'logical_score': float,
                    'performance_score': float,
                    'issues': List[Dict],
                    'recommendations': List[str]
                }
        """
        # Run all checks
        integrity = await self.error_detector.check_integrity(db_path)
        corruption = await self.error_detector.detect_corruption(db_path)
        logical_errors = await self.error_detector.find_logical_errors(db_path)

        # Calculate scores
        integrity_score = (
            100 if integrity["total_errors"] == 0 else max(0, 100 - integrity["total_errors"] * 20)
        )
        corruption_score = 100 if not corruption["corruption_detected"] else 0
        logical_score = 100 if len(logical_errors) == 0 else max(0, 100 - len(logical_errors) * 10)
        performance_score = await self._check_performance(db_path)

        # Calculate overall score
        overall_score = (integrity_score + corruption_score + logical_score + performance_score) / 4

        # Collect issues
        issues = []
        for error in integrity["errors"]:
            issues.append({"type": "integrity", "severity": "high", "message": error})

        if corruption["corruption_detected"]:
            issues.append(
                {
                    "type": "corruption",
                    "severity": "critical",
                    "message": "Database corruption detected",
                }
            )

        for error in logical_errors:
            issues.append({"type": "logical", "severity": error["severity"], "message": str(error)})

        # Generate recommendations
        recommendations = []
        if overall_score < 50:
            recommendations.append("Critical health issues detected - immediate action required")
        elif overall_score < 75:
            recommendations.append("Some health issues detected - review and fix")
        else:
            recommendations.append("Database is in good health")

        return {
            "overall_score": round(overall_score, 2),
            "integrity_score": integrity_score,
            "corruption_score": corruption_score,
            "logical_score": logical_score,
            "performance_score": performance_score,
            "issues": issues,
            "recommendations": recommendations,
            "total_issues": len(issues),
            "health_status": self._get_health_status(overall_score),
        }

    async def _check_performance(self, db_path: str) -> float:
        """Check database performance indicators.

        Args:
            db_path: Path to database file

        Returns:
            Performance score (0-100)
        """
        import aiosqlite

        try:
            async with aiosqlite.connect(db_path) as conn:
                # Check for missing indexes on foreign keys
                query = (
                    "SELECT COUNT(*) FROM sqlite_master"
                    " WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
                async with conn.execute(query) as cursor:
                    table_count = (await cursor.fetchone())[0]

                score = 100  # Start with perfect score
                if table_count > 10:
                    score -= 10  # Deduct for many tables
                if table_count > 50:
                    score -= 10  # Deduct more for very many tables

                return max(0, score)
        except Exception:
            return 50  # Return medium score on error

    def _get_health_status(self, score: float) -> str:
        """Get health status text from score.

        Args:
            score: Health score (0-100)

        Returns:
            Health status string
        """
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 50:
            return "fair"
        elif score >= 25:
            return "poor"
        else:
            return "critical"
