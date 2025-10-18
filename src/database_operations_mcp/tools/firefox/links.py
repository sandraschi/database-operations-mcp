"""Bookmark link management for Firefox."""

import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp

from .utils import get_places_db_path


@mcp.tool()
async def list_bookmarks(
    profile_name: Optional[str] = None,
    folder_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    """List bookmarks with optional folder filtering.

    Args:
        profile_name: Name of the Firefox profile
        folder_id: ID of the folder to list bookmarks from (None for all)
        limit: Maximum number of bookmarks to return
        offset: Offset for pagination

    Returns:
        Dictionary with bookmarks and metadata
    """
    places_db = get_places_db_path(profile_name)
    if not places_db or not places_db.exists():
        return {
            "status": "error",
            "message": (
                f"Could not find Firefox bookmarks database for profile: "
                f"{profile_name or 'default'}"
            ),
        }

    try:
        conn = sqlite3.connect(f"file:{places_db}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Build the query
        query = """
            SELECT b.id, b.title, p.url, b.dateAdded, b.lastModified, b.parent,
                   (SELECT title FROM moz_bookmarks WHERE id = b.parent) as folder
            FROM moz_bookmarks b
            JOIN moz_places p ON b.fk = p.id
            WHERE b.type = 1  -- Bookmarks
        """
        params = []

        if folder_id is not None:
            query += " AND b.parent = ?"
            params.append(folder_id)

        query += " ORDER BY b.lastModified DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        bookmarks = [dict(row) for row in cursor.fetchall()]

        # Get total count for pagination
        count_query = "SELECT COUNT(*) FROM moz_bookmarks WHERE type = 1"
        if folder_id is not None:
            count_query += " AND parent = ?"
            cursor.execute(count_query, (folder_id,))
        else:
            cursor.execute(count_query)
        total_count = cursor.fetchone()[0]

        return {
            "status": "success",
            "count": len(bookmarks),
            "total": total_count,
            "offset": offset,
            "bookmarks": bookmarks,
        }

    except sqlite3.Error as e:
        return {"status": "error", "message": f"Database error: {str(e)}"}
    finally:
        if "conn" in locals():
            conn.close()


@mcp.tool()
async def get_bookmark(bookmark_id: int, profile_name: Optional[str] = None) -> Dict[str, Any]:
    """Get details for a specific bookmark.

    Args:
        bookmark_id: ID of the bookmark to retrieve
        profile_name: Name of the Firefox profile

    Returns:
        Dictionary with bookmark details
    """
    places_db = get_places_db_path(profile_name)
    if not places_db or not places_db.exists():
        return {
            "status": "error",
            "message": (
                f"Could not find Firefox bookmarks database for profile: "
                f"{profile_name or 'default'}"
            ),
        }

    try:
        conn = sqlite3.connect(f"file:{places_db}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT b.id, b.title, p.url, b.dateAdded, b.lastModified, b.parent,
                   (SELECT title FROM moz_bookmarks WHERE id = b.parent) as folder,
                   p.visit_count, p.last_visit_date, p.description
            FROM moz_bookmarks b
            JOIN moz_places p ON b.fk = p.id
            WHERE b.id = ? AND b.type = 1
        """,
            (bookmark_id,),
        )

        bookmark = cursor.fetchone()
        if not bookmark:
            return {"status": "error", "message": f"Bookmark with ID {bookmark_id} not found"}

        # Get tags
        cursor.execute(
            """
            SELECT t.title as tag
            FROM moz_bookmarks t
            JOIN moz_bookmarks b ON b.id = ?
            JOIN moz_bookmarks b2 ON b2.parent = t.id
            WHERE t.parent = (SELECT id FROM moz_bookmarks WHERE title = 'tags' AND parent = 4)
            AND b2.fk = b.fk
        """,
            (bookmark_id,),
        )

        tags = [row[0] for row in cursor.fetchall()]

        bookmark_dict = dict(bookmark)
        # ... (continuing from previous code)

        # Add tags if provided
        if tags:
            for tag_name in tags:
                # Get or create tag
                cursor.execute(
                    "SELECT id FROM moz_bookmarks "
                    "WHERE parent = (SELECT id FROM moz_bookmarks "
                    "WHERE title = 'tags' AND parent = 4) "
                    "AND title = ?",
                    (tag_name,),
                )
                tag_row = cursor.fetchone()

                if not tag_row:
                    # Create new tag
                    cursor.execute(
                        "INSERT INTO moz_bookmarks "
                        "(type, parent, position, title, dateAdded, lastModified) "
                        "SELECT 2, id, "
                        "COALESCE((SELECT MAX(position) FROM moz_bookmarks "
                        "WHERE parent = id), 0) + 1, "
                        "?, ?, ? "
                        "FROM moz_bookmarks WHERE title = 'tags' AND parent = 4",
                        (tag_name, datetime.now(), datetime.now()),
                    )
                    tag_id = cursor.lastrowid
                else:
                    tag_id = tag_row[0]

                # Tag the bookmark
                cursor.execute(
                    "INSERT OR IGNORE INTO moz_bookmarks "
                    "(type, fk, parent, position, dateAdded, lastModified) "
                    "VALUES (1, ?, ?, 0, ?, ?)",
                    (bookmark_dict["fk"], tag_id, datetime.now(), datetime.now()),
                )

        # Commit transaction
        conn.commit()

        return {"status": "success", "bookmark_id": bookmark_id}

    except sqlite3.Error as e:
        if "conn" in locals():
            conn.rollback()
        return {"status": "error", "message": f"Database error: {str(e)}"}
    finally:
        if "conn" in locals():
            conn.close()


@mcp.tool()
async def add_bookmark(
    url: str,
    title: str,
    folder_id: int = 3,  # Default to "Other Bookmarks" folder
    tags: Optional[List[str]] = None,
    description: Optional[str] = None,
    profile_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a new bookmark to Firefox.

    Args:
        url: URL of the bookmark
        title: Title of the bookmark
        folder_id: ID of the folder to place the bookmark in (default: 3 = "Other Bookmarks")
        tags: Optional list of tags to apply
        description: Optional description for the bookmark
        profile_name: Name of the Firefox profile

    Returns:
        Dictionary with status and bookmark ID if successful
    """
    places_db = get_places_db_path(profile_name)
    if not places_db or not places_db.exists():
        return {
            "status": "error",
            "message": (
                f"Could not find Firefox bookmarks database for profile: "
                f"{profile_name or 'default'}"
            ),
        }

    try:
        conn = sqlite3.connect(f"file:{places_db}", uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Start transaction
        cursor.execute("BEGIN TRANSACTION")

        # Get or create the URL in moz_places
        cursor.execute("SELECT id, url FROM moz_places WHERE url = ?", (url,))
        place = cursor.fetchone()

        if place:
            place_id = place["id"]
        else:
            # Insert new place
            cursor.execute(
                "INSERT INTO moz_places (url, title, rev_host, hidden, typed, frecency) "
                "VALUES (?, ?, ?, 0, 1, -1)",
                (
                    url,
                    title,
                    "." + ".".join(reversed(url.split("://")[1].split("/")[0].split("."))),
                ),
            )
            place_id = cursor.lastrowid

        # Insert bookmark
        now = int(datetime.now().timestamp() * 1000000)  # microseconds since epoch
        cursor.execute(
            "INSERT INTO moz_bookmarks "
            "(type, fk, parent, position, title, dateAdded, lastModified) "
            "VALUES (1, ?, ?, "
            "COALESCE((SELECT MAX(position) FROM moz_bookmarks WHERE parent = ?), -1) + 1, "
            "?, ?, ?)",
            (place_id, folder_id, folder_id, title, now, now),
        )
        bookmark_id = cursor.lastrowid

        # Add description if provided
        if description:
            cursor.execute(
                "UPDATE moz_places SET description = ? WHERE id = ?", (description, place_id)
            )

        # Add tags if provided
        if tags:
            for tag_name in tags:
                # Get or create tag
                cursor.execute(
                    "SELECT id FROM moz_bookmarks "
                    "WHERE parent = (SELECT id FROM moz_bookmarks "
                    "WHERE title = 'tags' AND parent = 4) "
                    "AND title = ?",
                    (tag_name,),
                )
                tag_row = cursor.fetchone()

                if not tag_row:
                    # Create new tag
                    cursor.execute(
                        "INSERT INTO moz_bookmarks "
                        "(type, parent, position, title, dateAdded, lastModified) "
                        "SELECT 2, id, "
                        "COALESCE((SELECT MAX(position) FROM moz_bookmarks "
                        "WHERE parent = id), 0) + 1, "
                        "?, ?, ? "
                        "FROM moz_bookmarks WHERE title = 'tags' AND parent = 4",
                        (tag_name, now, now),
                    )
                    tag_id = cursor.lastrowid
                else:
                    tag_id = tag_row[0]

                # Tag the bookmark
                cursor.execute(
                    "INSERT OR IGNORE INTO moz_bookmarks "
                    "(type, fk, parent, position, dateAdded, lastModified) "
                    "VALUES (1, ?, ?, 0, ?, ?)",
                    (place_id, tag_id, now, now),
                )

        # Commit transaction
        conn.commit()

        return {"status": "success", "bookmark_id": bookmark_id, "place_id": place_id}

    except sqlite3.Error as e:
        if "conn" in locals():
            conn.rollback()
        return {"status": "error", "message": f"Database error: {str(e)}"}
    finally:
        if "conn" in locals():
            conn.close()
