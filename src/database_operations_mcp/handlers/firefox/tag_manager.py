"""Tag management for Firefox bookmarks."""
from pathlib import Path
from typing import List, Dict, Any
from .db import FirefoxDB
from fastmcp import tool

class TagManager:
    """Handles bookmark tagging operations."""
    
    def __init__(self, profile_path: Optional[Path] = None):
        self.db = FirefoxDB(profile_path)
        
    def get_tags(self) -> List[Dict[str, Any]]:
        """Get all tags with bookmark counts."""
        query = """
            SELECT t.id, t.title, COUNT(b2.id) as bookmark_count
            FROM moz_bookmarks t
            JOIN moz_bookmarks b2 ON b2.parent = t.id
            WHERE t.parent = (SELECT id FROM moz_bookmarks WHERE title = 'tags' AND parent = 4)
            GROUP BY t.id, t.title
        """
        cursor = self.db.execute(query)
        return [dict(row) for row in cursor.fetchall()]

@tool()
async def list_tags(profile_path: Optional[str] = None) -> Dict[str, Any]:
    """List all tags with bookmark counts."""
    try:
        manager = TagManager(Path(profile_path) if profile_path else None)
        tags = manager.get_tags()
        return {
            "status": "success",
            "count": len(tags),
            "tags": tags
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }