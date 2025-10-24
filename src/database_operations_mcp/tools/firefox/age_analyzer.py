"""Age analysis for Firefox bookmarks."""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp

from database_operations_mcp.tools.help_tools import HelpSystem
from .db import FirefoxDB


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def find_old_bookmarks(
    days_old: int = 365, profile_path: Optional[str] = None
) -> Dict[str, Any]:
    """Find bookmarks that haven't been visited in a while.

    Args:
        days_old: Minimum age in days to consider a bookmark "old"
        profile_path: Path to the Firefox profile directory

    Returns:
        Dictionary with old bookmarks and statistics
    """
    db = FirefoxDB(Path(profile_path) if profile_path else None)
    cutoff_date = datetime.now() - timedelta(days=days_old)
    cutoff_timestamp = int(cutoff_date.timestamp() * 1000000)  # Convert to microseconds

    query = """
        SELECT b.id, b.title, p.url, 
               p.last_visit_date / 1000000 as last_visit_ts,
               (strftime('%s', 'now') - p.last_visit_date/1000000)/86400 as days_since_visit
        FROM moz_places p
        JOIN moz_bookmarks b ON b.fk = p.id
        WHERE p.last_visit_date > 0
          AND p.last_visit_date < ?
        ORDER BY p.last_visit_date ASC
    """

    cursor = db.execute(query, (cutoff_timestamp,))
    old_bookmarks = []

    for row in cursor.fetchall():
        bookmark = dict(row)
        bookmark["last_visit_date"] = datetime.fromtimestamp(bookmark["last_visit_ts"]).isoformat()
        old_bookmarks.append(bookmark)

    return {
        "cutoff_date": cutoff_date.isoformat(),
        "bookmark_count": len(old_bookmarks),
        "bookmarks": old_bookmarks,
    }


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def get_bookmark_stats(profile_path: Optional[str] = None) -> Dict[str, Any]:
    """Get statistics about bookmark age and usage.

    Args:
        profile_path: Path to the Firefox profile directory

    Returns:
        Dictionary with bookmark statistics
    """
    db = FirefoxDB(Path(profile_path) if profile_path else None)

    # Get total bookmarks
    total_query = "SELECT COUNT(*) as count FROM moz_bookmarks WHERE type = 1"
    total = db.execute(total_query).fetchone()["count"]

    # Get bookmarks by age
    age_query = """
        SELECT 
            COUNT(*) as count,
            CASE 
                WHEN (strftime('%s', 'now') - p.last_visit_date/1000000) < 7 THEN '1_week'
                WHEN (strftime('%s', 'now') - p.last_visit_date/1000000) < 30 THEN '1_month'
                WHEN (strftime('%s', 'now') - p.last_visit_date/1000000) < 90 THEN '3_months'
                WHEN (strftime('%s', 'now') - p.last_visit_date/1000000) < 365 THEN '1_year'
                ELSE 'older'
            END as age_group
        FROM moz_places p
        JOIN moz_bookmarks b ON b.fk = p.id
        WHERE p.last_visit_date > 0
        GROUP BY age_group
    """

    cursor = db.execute(age_query)
    age_stats = {row["age_group"]: row["count"] for row in cursor.fetchall()}

    # Get most recently visited bookmarks
    recent_query = """
        SELECT b.title, p.url, p.last_visit_date / 1000000 as last_visit_ts
        FROM moz_places p
        JOIN moz_bookmarks b ON b.fk = p.id
        WHERE p.last_visit_date > 0
        ORDER BY p.last_visit_date DESC
        LIMIT 10
    """

    cursor = db.execute(recent_query)
    recent_bookmarks = []

    for row in cursor.fetchall():
        bookmark = dict(row)
        bookmark["last_visit_date"] = datetime.fromtimestamp(bookmark["last_visit_ts"]).isoformat()
        recent_bookmarks.append(bookmark)

    return {
        "total_bookmarks": total,
        "age_distribution": age_stats,
        "recently_visited": recent_bookmarks,
    }
