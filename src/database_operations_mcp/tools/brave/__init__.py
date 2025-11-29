"""Brave bookmark tools."""

from pathlib import Path
from typing import Any

from database_operations_mcp.config.mcp_config import mcp

from ..chromium_common import (
    BRAVE_BOOKMARK_PATHS,
    _find_first_existing,
    read_chromium_bookmarks,
    write_chromium_bookmark,
    edit_chromium_bookmark,
    delete_chromium_bookmark,
)


async def list_brave_bookmarks(bookmarks_path: str | None = None) -> dict[str, Any]:
    """List Brave bookmarks.

    Parameters:
        bookmarks_path: Optional override path to Brave Bookmarks JSON

    Returns:
        dict: {status, count, bookmarks}
    """
    path = (
        _find_first_existing(BRAVE_BOOKMARK_PATHS) if not bookmarks_path else Path(bookmarks_path)
    )
    return read_chromium_bookmarks(path)


async def add_brave_bookmark(
    title: str,
    url: str,
    folder: str | None = None,
    bookmarks_path: str | None = None,
) -> dict[str, Any]:
    """Add a bookmark to Brave Bookmarks JSON.

    Parameters:
        title: Bookmark title
        url: Bookmark URL
        folder: Optional target folder name
        bookmarks_path: Optional override path

    Returns:
        dict: {status, ...}
    """
    path = (
        _find_first_existing(BRAVE_BOOKMARK_PATHS) if not bookmarks_path else Path(bookmarks_path)
    )
    return write_chromium_bookmark(path, title, url, folder)


async def edit_brave_bookmark(
    *,
    id: str | None = None,
    url: str | None = None,
    new_title: str | None = None,
    new_folder: str | None = None,
    allow_duplicates: bool = False,
    create_folders: bool = True,
    dry_run: bool = False,
    bookmarks_path: str | None = None,
) -> dict[str, Any]:
    """Edit a Brave bookmark by id or url (rename/move)."""
    path = (
        _find_first_existing(BRAVE_BOOKMARK_PATHS) if not bookmarks_path else Path(bookmarks_path)
    )
    return edit_chromium_bookmark(
        path,
        id=id,
        url=url,
        new_title=new_title,
        new_folder=new_folder,
        allow_duplicates=allow_duplicates,
        create_folders=create_folders,
        dry_run=dry_run,
    )


async def delete_brave_bookmark(
    *,
    id: str | None = None,
    url: str | None = None,
    dry_run: bool = False,
    bookmarks_path: str | None = None,
) -> dict[str, Any]:
    """Delete a Brave bookmark by id or url."""
    path = (
        _find_first_existing(BRAVE_BOOKMARK_PATHS) if not bookmarks_path else Path(bookmarks_path)
    )
    return delete_chromium_bookmark(path, id=id, url=url, dry_run=dry_run)


# Register MCP tools without shadowing callables
LIST_BRAVE_BOOKMARKS_TOOL = mcp.tool(name="list_brave_bookmarks")(list_brave_bookmarks)
ADD_BRAVE_BOOKMARK_TOOL = mcp.tool(name="add_brave_bookmark")(add_brave_bookmark)
EDIT_BRAVE_BOOKMARK_TOOL = mcp.tool(name="edit_brave_bookmark")(edit_brave_bookmark)
DELETE_BRAVE_BOOKMARK_TOOL = mcp.tool(name="delete_brave_bookmark")(delete_brave_bookmark)
