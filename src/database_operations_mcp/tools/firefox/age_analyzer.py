"""Age analysis for Firefox bookmarks.

DEPRECATED: Individual tools deprecated. Use firefox_bookmarks portmanteau instead.
- find_old_bookmarks() → firefox_bookmarks(operation='find_old_bookmarks')
- find_forgotten_bookmarks() → firefox_bookmarks(operation='find_forgotten_bookmarks')
- get_bookmark_stats() → firefox_bookmarks(operation='get_bookmark_stats')
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# NOTE: @mcp.tool decorators removed - functionality moved to firefox_bookmarks portmanteau
from .db import FirefoxDB


# DEPRECATED: Use firefox_bookmarks(operation='find_old_bookmarks') instead
async def find_old_bookmarks(
    days_old: int = 365, profile_path: str | None = None
) -> dict[str, Any]:
    """Find bookmarks CREATED a long time ago (by dateAdded).

    Args:
        days_old: Minimum age in days since bookmark was CREATED
        profile_path: Path to the Firefox profile directory

    Returns:
        Dictionary with old bookmarks sorted by creation date (oldest first)
    """
    db = FirefoxDB(Path(profile_path) if profile_path else None)
    cutoff_date = datetime.now() - timedelta(days=days_old)
    cutoff_timestamp = int(cutoff_date.timestamp() * 1000000)  # Convert to microseconds

    query = """
        SELECT b.id, b.title, p.url, 
               b.dateAdded / 1000000 as created_ts,
               b.lastModified / 1000000 as modified_ts,
               (strftime('%s', 'now') - b.dateAdded/1000000)/86400 as age_days,
               (strftime('%s', 'now') - b.dateAdded/1000000)/86400/365.25 as age_years
        FROM moz_bookmarks b
        LEFT JOIN moz_places p ON b.fk = p.id
        WHERE b.type = 1
          AND b.dateAdded < ?
        ORDER BY b.dateAdded ASC
    """

    cursor = db.execute(query, (cutoff_timestamp,))
    old_bookmarks = []

    for row in cursor.fetchall():
        bookmark = dict(row)
        if bookmark["created_ts"]:
            bookmark["created"] = datetime.fromtimestamp(bookmark["created_ts"]).isoformat()
        if bookmark["modified_ts"]:
            bookmark["last_modified"] = datetime.fromtimestamp(bookmark["modified_ts"]).isoformat()
        bookmark["age_years"] = round(bookmark["age_years"], 1) if bookmark["age_years"] else None
        old_bookmarks.append(bookmark)

    return {
        "description": f"Bookmarks created more than {days_old} days ago",
        "cutoff_date": cutoff_date.isoformat(),
        "bookmark_count": len(old_bookmarks),
        "bookmarks": old_bookmarks,
    }


# DEPRECATED: Use firefox_bookmarks(operation='find_forgotten_bookmarks') instead
async def find_forgotten_bookmarks(
    days_unvisited: int = 365, profile_path: str | None = None
) -> dict[str, Any]:
    """Find bookmarks not VISITED in a while (by last_visit_date).
    
    These are bookmarks that exist but haven't been clicked/used.
    Good candidates for archiving or deletion.

    Args:
        days_unvisited: Minimum days since last visit
        profile_path: Path to the Firefox profile directory

    Returns:
        Dictionary with forgotten/unused bookmarks
    """
    db = FirefoxDB(Path(profile_path) if profile_path else None)
    cutoff_date = datetime.now() - timedelta(days=days_unvisited)
    cutoff_timestamp = int(cutoff_date.timestamp() * 1000000)  # Convert to microseconds

    query = """
        SELECT b.id, b.title, p.url, 
               p.last_visit_date / 1000000 as last_visit_ts,
               (strftime('%s', 'now') - p.last_visit_date/1000000)/86400 as days_since_visit
        FROM moz_places p
        JOIN moz_bookmarks b ON b.fk = p.id
        WHERE b.type = 1
          AND p.last_visit_date > 0
          AND p.last_visit_date < ?
        ORDER BY p.last_visit_date ASC
    """

    cursor = db.execute(query, (cutoff_timestamp,))
    stale_bookmarks = []

    for row in cursor.fetchall():
        bookmark = dict(row)
        bookmark["last_visit"] = datetime.fromtimestamp(bookmark["last_visit_ts"]).isoformat()
        stale_bookmarks.append(bookmark)

    return {
        "description": f"Bookmarks not visited in {days_unvisited}+ days",
        "cutoff_date": cutoff_date.isoformat(),
        "bookmark_count": len(stale_bookmarks),
        "bookmarks": stale_bookmarks,
    }


# DEPRECATED: Use firefox_bookmarks(operation='get_bookmark_stats') instead
async def get_bookmark_stats(profile_path: str | None = None) -> dict[str, Any]:
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
