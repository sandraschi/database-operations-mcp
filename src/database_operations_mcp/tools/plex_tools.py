"""
Plex Media Server Database Tools

DEPRECATED: This module is deprecated. Use media_library portmanteau tool instead.

All operations have been consolidated into media_library():
- find_plex_database() → media_library(operation='find_plex_database')
- optimize_plex_database() → media_library(operation='optimize_plex_database')
- export_database_schema() → media_library(operation='export_database_schema')
- get_plex_library_stats() → media_library(operation='get_plex_library_stats')

This module is kept for backwards compatibility but tools are no longer registered.
"""

import json
import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any


logger = logging.getLogger(__name__)

# Default Plex database locations
PLEX_DB_PATHS = {
    "windows": [
        r"%LOCALAPPDATA%\\Plex Media Server\\Plug-in Support\\"
        r"Databases\\com.plexapp.plugins.library.db",
        r"C:\\Plex\\Plex Media Server\\Plug-in Support\\Databases\\com.plexapp.plugins.library.db",
    ],
    "darwin": [
        "~/Library/Application Support/Plex Media Server/"
        "Plug-in Support/Databases/com.plexapp.plugins.library.db",
        "/var/lib/plex/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db",
    ],
    "linux": [
        "~/.local/share/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db",
        "/var/lib/plexmediaserver/Library/Application Support/"
        "Plex Media Server/Plug-in Support/Databases/"
        "com.plexapp.plugins.library.db",
    ],
}


class PlexDatabase:
    """Class for interacting with Plex Media Server's database."""

    def __init__(self, db_path: str | None = None):
        """Initialize with path to Plex database.

        Args:
            db_path: Path to the Plex database file. If not provided, will attempt
                   to find it automatically.
        """
        self.db_path = self._locate_database(db_path) if not db_path else Path(db_path)
        self.conn = None
        self.cursor = None

    def _locate_database(self, db_path: str | None = None) -> Path:
        """Attempt to locate the Plex database file."""
        if db_path and Path(db_path).exists():
            return Path(db_path)

        # Try platform-specific default locations
        import platform

        system = platform.system().lower()

        paths = []
        if "windows" in system:
            paths = PLEX_DB_PATHS["windows"]
        elif "darwin" in system:
            paths = PLEX_DB_PATHS["darwin"]
        else:  # Linux/Unix
            paths = PLEX_DB_PATHS["linux"]

        # Expand environment variables and home directory
        paths = [os.path.expanduser(os.path.expandvars(p)) for p in paths]

        # Check each possible location
        for path in paths:
            path = Path(path)
            if path.exists():
                return path

        raise FileNotFoundError("Could not locate Plex database. Please specify the path manually.")

    def connect(self):
        """Connect to the Plex database."""
        if self.conn is None:
            self.conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get_library_sections(self) -> list[dict[str, Any]]:
        """Get a list of all library sections."""
        self.connect()
        self.cursor.execute("""
            SELECT id, name, section_type, language, agent, scanner, 
                   created_at, updated_at, scanned_at
            FROM library_sections
            ORDER BY name
        """)
        return [dict(row) for row in self.cursor.fetchall()]

    def get_media_items(
        self, section_id: int | None = None, limit: int = 100, offset: int = 0
    ) -> list[dict[str, Any]]:
        """Get media items from the library.

        Args:
            section_id: Filter by library section ID. If None, returns all sections.
            limit: Maximum number of items to return.
            offset: Offset for pagination.

        Returns:
            List of media items with metadata.
        """
        self.connect()
        query = """
            SELECT mi.id, mi.library_section_id, ls.name as section_name,
                   mi.metadata_type, mi.guid, mi.media_item_title, 
                   mi.summary, mi.rating, mi.view_count, mi.last_viewed_at,
                   mi.duration, mi.bitrate, mi.width, mi.height,
                   mi.frames_per_second, mi.audio_channels,
                   mi.audio_codec, mi.video_codec, mi.container,
                   mi.file_size, mi.created_at, mi.updated_at
            FROM media_items mi
            LEFT JOIN library_sections ls ON mi.library_section_id = ls.id
        """
        params = []

        if section_id is not None:
            query += " WHERE mi.library_section_id = ?"
            params.append(section_id)

        query += " ORDER BY mi.media_item_title"
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]

    def export_library(
        self, output_format: str = "json", output_path: str | Path | None = None
    ) -> dict[str, Any]:
        """Export the Plex library to a file.

        Args:
            output_format: Output format ('json', 'csv', or 'sqlite').
            output_path: Path to save the exported file. If None, returns the data.

        Returns:
            Dictionary with export results.
        """
        try:
            self.connect()

            # Get all library sections
            sections = self.get_library_sections()

            # Get media items for each section
            library_data = {
                "metadata": {
                    "export_date": datetime.utcnow().isoformat(),
                    "plex_db_path": str(self.db_path),
                    "section_count": len(sections),
                },
                "sections": [],
            }

            for section in sections:
                section_data = dict(section)
                section_data["media_items"] = self.get_media_items(section_id=section["id"])
                library_data["sections"].append(section_data)

            # Handle output
            if output_path:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)

                if output_format == "json":
                    with open(output_path, "w", encoding="utf-8") as f:
                        json.dump(library_data, f, indent=2, ensure_ascii=False)

                elif output_format == "csv":
                    # Flatten the data for CSV
                    import csv

                    # Create a flat structure for CSV
                    flat_data = []
                    for section in library_data["sections"]:
                        for item in section["media_items"]:
                            flat_item = {
                                "section_id": section["id"],
                                "section_name": section["name"],
                                **{k: v for k, v in item.items() if k != "section_name"},
                            }
                            flat_data.append(flat_item)

                    if flat_data:
                        with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
                            writer = csv.DictWriter(f, fieldnames=flat_data[0].keys())
                            writer.writeheader()
                            writer.writerows(flat_data)

                elif output_format == "sqlite":
                    # Create a new SQLite database
                    import sqlite3
                    from sqlite3 import Error as SqliteError

                    try:
                        conn = sqlite3.connect(str(output_path))
                        cursor = conn.cursor()

                        # Create tables
                        cursor.execute("""
                            CREATE TABLE IF NOT EXISTS sections (
                                id INTEGER PRIMARY KEY,
                                name TEXT,
                                section_type INTEGER,
                                agent TEXT,
                                created_at TEXT,
                                updated_at TEXT,
                                scanned_at TEXT
                            )
                        """)

                        cursor.execute("""
                            CREATE TABLE IF NOT EXISTS media_items (
                                id INTEGER PRIMARY KEY,
                                section_id INTEGER,
                                section_name TEXT,
                                metadata_type INTEGER,
                                guid TEXT,
                                media_item_title TEXT,
                                summary TEXT,
                                rating REAL,
                                view_count INTEGER,
                                last_viewed_at TEXT,
                                duration INTEGER,
                                bitrate INTEGER,
                                width INTEGER,
                                height INTEGER,
                                frames_per_second REAL,
                                audio_channels INTEGER,
                                audio_codec TEXT,
                                video_codec TEXT,
                                container TEXT,
                                file_size INTEGER,
                                created_at TEXT,
                                updated_at TEXT,
                                FOREIGN KEY (section_id) REFERENCES sections (id)
                            )
                        """)

                        # Insert sections
                        for section in library_data["sections"]:
                            cursor.execute(
                                """
                                INSERT INTO sections (
                                    id, name, section_type, agent, 
                                    created_at, updated_at, scanned_at
                                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                            """,
                                (
                                    section["id"],
                                    section["name"],
                                    section.get("section_type"),
                                    section.get("agent"),
                                    section.get("created_at"),
                                    section.get("updated_at"),
                                    section.get("scanned_at"),
                                ),
                            )

                            # Insert media items
                            for item in section["media_items"]:
                                cursor.execute(
                                    """
                                    INSERT INTO media_items (
                                        id, section_id, section_name, metadata_type, guid,
                                        media_item_title, summary, rating, view_count,
                                        last_viewed_at, duration, bitrate, width, height,
                                        frames_per_second, audio_channels, audio_codec,
                                        video_codec, container, file_size, created_at, updated_at
                                    ) VALUES (
                                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                                    )
                                """,
                                    (
                                        item["id"],
                                        section["id"],
                                        section["name"],
                                        item.get("metadata_type"),
                                        item.get("guid"),
                                        item.get("media_item_title"),
                                        item.get("summary"),
                                        item.get("rating"),
                                        item.get("view_count"),
                                        item.get("last_viewed_at"),
                                        item.get("duration"),
                                        item.get("bitrate"),
                                        item.get("width"),
                                        item.get("height"),
                                        item.get("frames_per_second"),
                                        item.get("audio_channels"),
                                        item.get("audio_codec"),
                                        item.get("video_codec"),
                                        item.get("container"),
                                        item.get("file_size"),
                                        item.get("created_at"),
                                        item.get("updated_at"),
                                    ),
                                )

                        conn.commit()
                        conn.close()

                    except SqliteError as e:
                        return {
                            "status": "error",
                            "message": f"SQLite error during export: {str(e)}",
                            "export_path": str(output_path),
                            "format": output_format,
                        }

                return {
                    "status": "success",
                    "message": f"Successfully exported Plex library to {output_path}",
                    "export_path": str(output_path),
                    "format": output_format,
                    "section_count": len(sections),
                    "total_items": sum(len(s["media_items"]) for s in library_data["sections"]),
                }

            return {
                "status": "success",
                "data": library_data,
                "section_count": len(sections),
                "total_items": sum(len(s["media_items"]) for s in library_data["sections"]),
            }

        except Exception as e:
            logger.exception("Error exporting Plex library")
            return {
                "status": "error",
                "message": f"Failed to export Plex library: {str(e)}",
                "error": str(e),
            }


def register_tools(mcp):
    """Register Plex Media Server tools with the MCP server.

    Args:
        mcp: The MCP server instance to register tools with.
    """


# DEPRECATED: Use media_library portmanteau instead
def get_plex_library_sections(db_path: str | None = None) -> list[dict[str, Any]]:
    """Get a list of all library sections from Plex.

    Args:
        db_path: Path to the Plex database file. If not provided, will attempt
               to find it automatically.

    Returns:
        A list of library sections with their metadata.
    """
    try:
        with PlexDatabase(db_path) as plex_db:
            return {"status": "success", "sections": plex_db.get_library_sections()}
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get Plex library sections: {str(e)}",
            "error": str(e),
        }
