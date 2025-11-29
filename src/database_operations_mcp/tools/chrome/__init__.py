"""Chrome bookmark tools."""

from pathlib import Path
from typing import Any

from database_operations_mcp.config.mcp_config import mcp

from ..chromium_common import (
    CHROME_BOOKMARK_PATHS,
    _find_first_existing,
    read_chromium_bookmarks,
    write_chromium_bookmark,
    edit_chromium_bookmark,
    delete_chromium_bookmark,
)


async def list_chrome_bookmarks(bookmarks_path: str | None = None) -> dict[str, Any]:
    """List Chrome bookmarks.

    Parameters:
        bookmarks_path: Optional override path to Chrome Bookmarks JSON

    Returns:
        dict: {status, count, bookmarks}
    """
    path = (
        _find_first_existing(CHROME_BOOKMARK_PATHS) if not bookmarks_path else Path(bookmarks_path)
    )
    return read_chromium_bookmarks(path)


async def add_chrome_bookmark(
    title: str,
    url: str,
    folder: str | None = None,
    bookmarks_path: str | None = None,
) -> dict[str, Any]:
    """Add a bookmark to Chrome Bookmarks JSON.

    Parameters:
        title: Bookmark title
        url: Bookmark URL
        folder: Optional target folder name
        bookmarks_path: Optional override path

    Returns:
        dict: {status, ...}
    """
    path = (
        _find_first_existing(CHROME_BOOKMARK_PATHS) if not bookmarks_path else Path(bookmarks_path)
    )
    return write_chromium_bookmark(path, title, url, folder)


async def edit_chrome_bookmark(
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
    """Edit a Chrome bookmark by id or url (rename/move)."""
    path = (
        _find_first_existing(CHROME_BOOKMARK_PATHS) if not bookmarks_path else Path(bookmarks_path)
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


async def delete_chrome_bookmark(
    *,
    id: str | None = None,
    url: str | None = None,
    dry_run: bool = False,
    bookmarks_path: str | None = None,
) -> dict[str, Any]:
    """Delete a Chrome bookmark by id or url."""
    path = (
        _find_first_existing(CHROME_BOOKMARK_PATHS) if not bookmarks_path else Path(bookmarks_path)
    )
    return delete_chromium_bookmark(path, id=id, url=url, dry_run=dry_run)


# Register MCP tools without shadowing callables
# NOTE: Keep these - chrome_bookmarks portmanteau doesn't have full CRUD yet
LIST_CHROME_BOOKMARKS_TOOL = mcp.tool(name="list_chrome_bookmarks")(list_chrome_bookmarks)
ADD_CHROME_BOOKMARK_TOOL = mcp.tool(name="add_chrome_bookmark")(add_chrome_bookmark)
EDIT_CHROME_BOOKMARK_TOOL = mcp.tool(name="edit_chrome_bookmark")(edit_chrome_bookmark)
DELETE_CHROME_BOOKMARK_TOOL = mcp.tool(name="delete_chrome_bookmark")(delete_chrome_bookmark)
