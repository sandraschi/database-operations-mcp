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
        
        search_term = f"%{query}%"
        query_sql = """
            SELECT b.id, b.title, p.url, b.dateAdded, b.lastModified, b.parent
            FROM moz_bookmarks b
            JOIN moz_places p ON b.fk = p.id
            WHERE b.type = 1
            AND (b.title LIKE ? OR p.url LIKE ?)
            ORDER BY b.lastModified DESC
            LIMIT ?
        """
        
        cursor.execute(query_sql, (search_term, search_term, max_results))
        results = [dict(row) for row in cursor.fetchall()]
        
        return {
            "status": "success",
            "query": query,
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
        
        if compare == "url":
            group_by = "p.url"
            select_fields = "p.url as value"
        elif compare == "title":
            group_by = "b.title"
            select_fields = "b.title as value"
        elif compare == "both":
            group_by = "b.title, p.url"
            select_fields = "b.title || '|' || p.url as value"
        else:
            return {
                "status": "error",
                "message": "Invalid comparison field. Use 'url', 'title', or 'both'"
            }
        
        # Find duplicate values
        dup_query = f"""
            SELECT {select_fields}, COUNT(*) as count
            FROM moz_bookmarks b
            JOIN moz_places p ON b.fk = p.id
            WHERE b.type = 1
            GROUP BY {group_by}
            HAVING COUNT(*) > 1
            ORDER BY count DESC
        """
        
        cursor.execute(dup_query)
        duplicates = cursor.fetchall()
        
        # Get all bookmarks for each duplicate value
        results = []
        for dup in duplicates:
            value = dup['value']
            
            if compare == "both":
                title, url = value.split('|', 1)
                where_clause = "b.title = ? AND p.url = ?"
                params = (title, url)
            else:
                where_clause = f"{group_by} = ?"
                params = (value,)
            
            bookmarks_query = f"""
                SELECT b.id, b.title, p.url, b.dateAdded, b.lastModified, b.parent
                FROM moz_bookmarks b
                JOIN moz_places p ON b.fk = p.id
                WHERE b.type = 1 AND {where_clause}
                ORDER BY b.lastModified DESC
            """
            
            cursor.execute(bookmarks_query, params)
            bookmarks = [dict(row) for row in cursor.fetchall()]
            
            results.append({
                'value': value,
                'count': len(bookmarks),
                'bookmarks': bookmarks
            })
        
        return {
            "status": "success",
            "compare_by": compare,
            "duplicate_count": len(duplicates),
            "duplicates": results
        }
        
    except sqlite3.Error as e:
        return {
            "status": "error",
            "message": f"Database error: {str(e)}"
        }
    finally:
        if 'conn' in locals():
            conn.close()