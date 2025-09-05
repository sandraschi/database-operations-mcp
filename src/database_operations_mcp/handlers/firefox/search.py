"""Search functionality for Firefox bookmarks."""
from pathlib import Path
from typing import Dict, Any, Optional, List
import sqlite3
from fastmcp import FastMCP
from .utils import get_places_db_path

@FastMCP.tool
async def search_bookmarks(
    query: str,
    profile_name: Optional[str] = None,
    max_results: int = 50
) -> Dict[str, Any]:
    """Search bookmarks by title or URL.
    
    Args:
        query: Search term to look for in bookmark titles and URLs
        profile_name: Name of the Firefox profile to search (defaults to default profile)
        max_results: Maximum number of results to return
        
    Returns:
        Dictionary containing search results
    """
    places_db = get_places_db_path(profile_name)
    if not places_db or not places_db.exists():
        return {
            "status": "error",
            "message": f"Could not find Firefox bookmarks database for profile: {profile_name or 'default'}"
        }
    
    try:
        conn = sqlite3.connect(f"file:{places_db}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Search in both title and URL
        search_term = f"%{query}%"
        cursor.execute("""
            SELECT b.id, b.title, p.url, b.dateAdded, b.lastModified,
                   (SELECT title FROM moz_bookmarks WHERE id = b.parent) as folder
            FROM moz_bookmarks b
            JOIN moz_places p ON b.fk = p.id
            WHERE b.type = 1  -- Bookmarks
            AND (b.title LIKE ? OR p.url LIKE ?)
            ORDER BY b.lastModified DESC
            LIMIT ?
        """, (search_term, search_term, max_results))
        
        results = [dict(row) for row in cursor.fetchall()]
        
        return {
            "status": "success",
            "count": len(results),
            "results": results
        }
        
    except sqlite3.Error as e:
        return {
            "status": "error",
            "message": f"Database error: {str(e)}"
        }
    finally:
        if 'conn' in locals():
            conn.close()

@FastMCP.tool
async def find_duplicates(
    profile_name: Optional[str] = None,
    compare: str = "url"  # or "title" or "both"
) -> Dict[str, Any]:
    """Find duplicate bookmarks.
    
    Args:
        profile_name: Name of the Firefox profile to search
        compare: Field to compare for duplicates: "url", "title", or "both"
        
    Returns:
        Dictionary with duplicate bookmarks grouped by the compared field
    """
    places_db = get_places_db_path(profile_name)
    if not places_db or not places_db.exists():
        return {
            "status": "error",
            "message": f"Could not find Firefox bookmarks database for profile: {profile_name or 'default'}"
        }
    
    try:
        conn = sqlite3.connect(f"file:{places_db}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Build the GROUP BY and HAVING clauses based on comparison type
        if compare == "url":
            group_by = "p.url"
            select = "p.url as match_value, p.url"
        elif compare == "title":
            group_by = "b.title"
            select = "b.title as match_value, '' as url"
        else:  # both
            group_by = "b.title, p.url"
            select = "b.title || '|' || p.url as match_value, p.url"
        
        # Find duplicates
        cursor.execute(f"""
            WITH duplicates AS (
                SELECT {select}, 
                       GROUP_CONCAT(b.id) as bookmark_ids,
                       COUNT(*) as count
                FROM moz_bookmarks b
                JOIN moz_places p ON b.fk = p.id
                WHERE b.type = 1  -- Bookmarks
                GROUP BY {group_by}
                HAVING COUNT(*) > 1
            )
            SELECT * FROM duplicates
            ORDER BY count DESC
        """)
        
        duplicates = {}
        for row in cursor.fetchall():
            row_dict = dict(row)
            match_value = row_dict.pop('match_value')
            duplicates[match_value] = {
                "count": row_dict.pop('count'),
                "url": row_dict.pop('url', ''),
                "bookmark_ids": [int(id) for id in row_dict.pop('bookmark_ids').split(',')]
            }
        
        return {
            "status": "success",
            "duplicate_count": len(duplicates),
            "duplicates": duplicates
        }
        
    except sqlite3.Error as e:
        return {
            "status": "error",
            "message": f"Database error: {str(e)}"
        }
    finally:
        if 'conn' in locals():
            conn.close()