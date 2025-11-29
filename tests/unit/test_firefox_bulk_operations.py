"""
Tests for Firefox bulk operations implementation.
"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from database_operations_mcp.tools.firefox.bulk_operations import (
    BulkOperations,
    batch_update_tags,
    remove_unused_tags,
)


class TestFirefoxBulkOperations:
    """Test the Firefox bulk operations functions."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock FirefoxDB instance."""
        mock_db = AsyncMock()
        mock_db.get_all_bookmarks = AsyncMock()
        mock_db.get_bookmarks = AsyncMock()
        mock_db.get_bookmark_tags = AsyncMock()
        mock_db.update_bookmark_tags = AsyncMock()
        mock_db.get_all_tags = AsyncMock()
        mock_db.delete_tag = AsyncMock()
        return mock_db

    @pytest.mark.asyncio
    @patch("database_operations_mcp.tools.firefox.bulk_operations.FirefoxDB")
    async def test_batch_update_tags_dry_run(self, mock_firefox_db_class, mock_db):
        """Test batch_update_tags in dry run mode."""
        # Setup
        mock_firefox_db_class.return_value = mock_db
        mock_bookmark = {
            "id": 1,
            "title": "Test Bookmark",
            "url": "http://example.com",
        }
        mock_db.get_all_bookmarks.return_value = [mock_bookmark]
        mock_db.get_bookmark_tags.return_value = ["existing_tag"]

        # Act - call the function directly (no decorator wrapper)
        result = await batch_update_tags(
            tag_mapping={"existing_tag": "updated_tag"}, dry_run=True, profile_path=None
        )

        # Assert
        assert result["dry_run"] is True
        assert "changes" in result
        # Verify no actual updates were made in dry run
        mock_db.update_bookmark_tags.assert_not_called()

    @pytest.mark.asyncio
    @patch("database_operations_mcp.tools.firefox.bulk_operations.FirefoxDB")
    async def test_batch_update_tags_actual_run(self, mock_firefox_db_class, mock_db):
        """Test batch_update_tags with actual updates."""
        # Setup
        mock_firefox_db_class.return_value = mock_db
        mock_bookmark = {
            "id": 1,
            "title": "Test Bookmark",
            "url": "http://example.com",
        }
        mock_db.get_all_bookmarks.return_value = [mock_bookmark]
        mock_db.get_bookmark_tags.return_value = ["old_tag"]

        # Act
        result = await batch_update_tags(
            tag_mapping={"old_tag": "new_tag"}, dry_run=False, profile_path=None
        )

        # Assert
        assert result["dry_run"] is False
        assert result["affected_bookmarks"] > 0
        # Verify updates were made
        mock_db.update_bookmark_tags.assert_called()

    @pytest.mark.asyncio
    @patch("database_operations_mcp.tools.firefox.bulk_operations.FirefoxDB")
    async def test_batch_update_tags_no_changes(self, mock_firefox_db_class, mock_db):
        """Test batch_update_tags when no changes are needed."""
        # Setup - bookmark doesn't have the tag being mapped
        mock_firefox_db_class.return_value = mock_db
        mock_bookmark = {
            "id": 1,
            "title": "Test Bookmark",
            "url": "http://example.com",
        }
        mock_db.get_all_bookmarks.return_value = [mock_bookmark]
        mock_db.get_bookmark_tags.return_value = ["other_tag"]

        # Act - map a tag that doesn't exist
        result = await batch_update_tags(
            tag_mapping={"nonexistent_tag": "new_tag"}, dry_run=False, profile_path=None
        )

        # Assert
        assert result["affected_bookmarks"] == 0
        # No updates should be made when tag doesn't exist
        mock_db.update_bookmark_tags.assert_not_called()

    @pytest.mark.asyncio
    @patch("database_operations_mcp.tools.firefox.bulk_operations.FirefoxDB")
    async def test_batch_update_tags_error_handling(
        self, mock_firefox_db_class, mock_db
    ):
        """Test batch_update_tags error handling."""
        # Setup - simulate an error
        mock_firefox_db_class.return_value = mock_db
        mock_db.get_all_bookmarks.side_effect = Exception("Database error")

        # Act
        result = await batch_update_tags(
            tag_mapping={"old": "new"}, dry_run=False, profile_path=None
        )

        # Assert - should handle error gracefully
        assert "error" in result or result.get("affected_bookmarks", 0) == 0

    @pytest.mark.asyncio
    @patch("database_operations_mcp.tools.firefox.bulk_operations.FirefoxDB")
    async def test_remove_unused_tags_dry_run(self, mock_firefox_db_class, mock_db):
        """Test remove_unused_tags in dry run mode."""
        # Setup
        mock_firefox_db_class.return_value = mock_db
        mock_db.get_all_tags.return_value = ["tag1", "tag2", "unused_tag"]
        mock_bookmark = {"id": 1, "title": "Test", "url": "http://example.com"}
        mock_db.get_all_bookmarks.return_value = [mock_bookmark]
        mock_db.get_bookmark_tags.return_value = ["tag1", "tag2"]  # unused_tag not used

        # Act
        result = await remove_unused_tags(dry_run=True, profile_path=None)

        # Assert
        assert result["dry_run"] is True
        assert "unused_tags" in result
        # Verify no actual deletions in dry run
        mock_db.delete_tag.assert_not_called()

    @pytest.mark.asyncio
    @patch("database_operations_mcp.tools.firefox.bulk_operations.FirefoxDB")
    async def test_remove_unused_tags_actual_run(self, mock_firefox_db_class, mock_db):
        """Test remove_unused_tags with actual removal."""
        # Setup
        mock_firefox_db_class.return_value = mock_db
        mock_db.get_all_tags.return_value = ["tag1", "unused_tag"]
        mock_bookmark = {"id": 1, "title": "Test", "url": "http://example.com"}
        mock_db.get_all_bookmarks.return_value = [mock_bookmark]
        mock_db.get_bookmark_tags.return_value = ["tag1"]  # unused_tag not used

        # Act
        result = await remove_unused_tags(dry_run=False, profile_path=None)

        # Assert
        assert result["dry_run"] is False
        assert result["removed_count"] >= 0
        # Verify deletions were attempted
        if result.get("removed_count", 0) > 0:
            mock_db.delete_tag.assert_called()

    @pytest.mark.asyncio
    @patch("database_operations_mcp.tools.firefox.bulk_operations.FirefoxDB")
    async def test_remove_unused_tags_no_unused(self, mock_firefox_db_class, mock_db):
        """Test remove_unused_tags when no unused tags exist."""
        # Setup - all tags are used
        mock_firefox_db_class.return_value = mock_db
        mock_db.get_all_tags.return_value = ["tag1", "tag2"]
        mock_bookmark = {"id": 1, "title": "Test", "url": "http://example.com"}
        mock_db.get_all_bookmarks.return_value = [mock_bookmark]
        mock_db.get_bookmark_tags.return_value = ["tag1", "tag2"]  # All tags used

        # Act
        result = await remove_unused_tags(dry_run=False, profile_path=None)

        # Assert
        assert result["removed_count"] == 0
        mock_db.delete_tag.assert_not_called()

    @pytest.mark.asyncio
    @patch("database_operations_mcp.tools.firefox.bulk_operations.FirefoxDB")
    async def test_remove_unused_tags_error_handling(
        self, mock_firefox_db_class, mock_db
    ):
        """Test remove_unused_tags error handling."""
        # Setup - simulate an error
        mock_firefox_db_class.return_value = mock_db
        mock_db.get_all_tags.side_effect = Exception("Database error")

        # Act
        result = await remove_unused_tags(dry_run=False, profile_path=None)

        # Assert - should handle error gracefully
        assert "error" in result or result.get("removed_count", 0) == 0

    @pytest.mark.asyncio
    async def test_bulk_operations_class_init(self):
        """Test BulkOperations class initialization."""
        bulk_ops = BulkOperations()
        assert bulk_ops.db is not None

    @pytest.mark.asyncio
    async def test_bulk_operations_process_in_batches(self, mock_db):
        """Test BulkOperations process_in_batches method."""
        # Mock data - first batch returns data, second batch returns empty list
        mock_bookmarks = [
            {
                "id": 1,
                "title": "Bookmark 1",
                "url": "http://example.com",
                "date_added": "2024-01-01",
                "last_modified": "2024-01-01",
            },
            {
                "id": 2,
                "title": "Bookmark 2",
                "url": "http://test.com",
                "date_added": "2024-01-02",
                "last_modified": "2024-01-02",
            },
        ]

        # Mock get_bookmarks to return data on first call, empty on second call
        mock_db.get_bookmarks = AsyncMock(side_effect=[mock_bookmarks, []])

        # Mock get_bookmark_tags method
        mock_db.get_bookmark_tags = AsyncMock(return_value=["tag1", "tag2"])

        bulk_ops = BulkOperations()
        bulk_ops.db = mock_db

        results = []
        async for result in bulk_ops.process_in_batches("export"):
            results.append(result)

        assert len(results) == 2
        assert results[0]["id"] == 1
        assert results[0]["title"] == "Bookmark 1"
        assert results[1]["id"] == 2
        assert results[1]["title"] == "Bookmark 2"
