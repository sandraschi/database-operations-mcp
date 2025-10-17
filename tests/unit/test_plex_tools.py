"""Unit tests for Plex Media Server tools."""

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from database_operations_mcp.tools.plex_tools import PlexDatabase, export_plex_library


class TestPlexDatabase(unittest.TestCase):
    """Test cases for PlexDatabase class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_plex.db"
        self._create_test_database()

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def _create_test_database(self):
        """Create a test SQLite database with Plex-like schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tables with a simplified Plex schema
        cursor.execute("""
            CREATE TABLE library_sections (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                section_type INTEGER,
                language TEXT,
                agent TEXT,
                scanner TEXT,
                created_at TEXT,
                updated_at TEXT,
                scanned_at TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE media_items (
                id INTEGER PRIMARY KEY,
                library_section_id INTEGER,
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
                FOREIGN KEY (library_section_id) REFERENCES library_sections(id)
            )
        """)

        # Insert test data
        cursor.execute(
            """
            INSERT INTO library_sections 
            (id, name, section_type, agent, created_at, updated_at)
            VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
        """,
            (1, "Movies", 1, "tv.plex.agents.movie"),
        )

        cursor.execute(
            """
            INSERT INTO media_items 
            (id, library_section_id, metadata_type, media_item_title, 
             summary, rating, view_count, duration, 
             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """,
            (1, 1, 1, "Test Movie", "A test movie", 8.5, 10, 5400),
        )

        conn.commit()
        conn.close()

    def test_init_with_explicit_path(self):
        """Test initialization with explicit database path."""
        db = PlexDatabase(str(self.db_path))
        self.assertEqual(db.db_path, self.db_path)

    @patch("os.path.exists")
    @patch("platform.system")
    def test_init_auto_detect_windows(self, mock_system, mock_exists):
        """Test automatic database detection on Windows."""
        mock_system.return_value = "Windows"
        test_path = r"C:\\Plex\\Plex Media Server\\Plug-in Support\\Databases\\com.plexapp.plugins.library.db"
        mock_exists.side_effect = lambda x: x == test_path

        db = PlexDatabase()
        self.assertEqual(db.db_path, Path(test_path))

    def test_connect(self):
        """Test database connection."""
        db = PlexDatabase(str(self.db_path))
        with db:
            self.assertIsNotNone(db.conn)
            self.assertIsNotNone(db.cursor)
        self.assertIsNone(db.conn)

    def test_get_library_sections(self):
        """Test getting library sections."""
        with PlexDatabase(str(self.db_path)) as db:
            sections = db.get_library_sections()
            self.assertEqual(len(sections), 1)
            self.assertEqual(sections[0]["name"], "Movies")

    def test_get_media_items(self):
        """Test getting media items."""
        with PlexDatabase(str(self.db_path)) as db:
            items = db.get_media_items(section_id=1)
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0]["media_item_title"], "Test Movie")


class TestExportPlexLibrary(unittest.TestCase):
    """Test cases for export_plex_library function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_plex.db"

        # Create a test database
        db = PlexDatabase(str(self.db_path))
        self._create_test_database(db)

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def _create_test_database(self, db):
        """Create a test database with sample data."""
        cursor = db.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS library_sections (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                section_type INTEGER
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS media_items (
                id INTEGER PRIMARY KEY,
                library_section_id INTEGER,
                media_item_title TEXT,
                FOREIGN KEY (library_section_id) REFERENCES library_sections(id)
            )
        """)
        cursor.execute(
            "INSERT INTO library_sections (id, name, section_type) VALUES (1, 'Test Section', 1)"
        )
        cursor.execute(
            "INSERT INTO media_items (id, library_section_id, media_item_title) VALUES (1, 1, 'Test Item')"
        )
        db.conn.commit()

    def test_export_json(self):
        """Test exporting to JSON format."""
        output_path = Path(self.temp_dir.name) / "export.json"
        result = export_plex_library(
            db_path=str(self.db_path), output_format="json", output_path=str(output_path)
        )

        self.assertEqual(result["status"], "success")
        self.assertTrue(output_path.exists())
        self.assertGreater(os.path.getsize(output_path), 0)

    def test_export_csv(self):
        """Test exporting to CSV format."""
        output_path = Path(self.temp_dir.name) / "export.csv"
        result = export_plex_library(
            db_path=str(self.db_path), output_format="csv", output_path=str(output_path)
        )

        self.assertEqual(result["status"], "success")
        self.assertTrue(output_path.exists())
        self.assertGreater(os.path.getsize(output_path), 0)

    def test_export_sqlite(self):
        """Test exporting to SQLite format."""
        output_path = Path(self.temp_dir.name) / "export.db"
        result = export_plex_library(
            db_path=str(self.db_path), output_format="sqlite", output_path=str(output_path)
        )

        self.assertEqual(result["status"], "success")
        self.assertTrue(output_path.exists())

        # Verify the exported SQLite database
        conn = sqlite3.connect(f"file:{output_path}?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sections")
        section_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM media_items")
        item_count = cursor.fetchone()[0]
        conn.close()

        self.assertEqual(section_count, 1)
        self.assertEqual(item_count, 1)

    def test_export_invalid_format(self):
        """Test exporting with an invalid format."""
        with self.assertRaises(ValueError):
            export_plex_library(
                db_path=str(self.db_path),
                output_format="invalid_format",
                output_path=str(Path(self.temp_dir.name) / "export.txt"),
            )

    def test_export_nonexistent_db(self):
        """Test exporting with a non-existent database."""
        result = export_plex_library(
            db_path="/nonexistent/path/to/plex.db",
            output_format="json",
            output_path=str(Path(self.temp_dir.name) / "export.json"),
        )

        self.assertEqual(result["status"], "error")
        self.assertIn("not found", result["message"].lower())
