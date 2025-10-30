"""Edge bookmark tools."""

from pathlib import Path
from typing import Any

from database_operations_mcp.config.mcp_config import mcp

from ..chromium_common import (
    EDGE_BOOKMARK_PATHS,
    _find_first_existing,
    read_chromium_bookmarks,
    write_chromium_bookmark,
    edit_chromium_bookmark,
    delete_chromium_bookmark,
)


async def list_edge_bookmarks(bookmarks_path: str | None = None) -> dict[str, Any]:
    """List Microsoft Edge bookmarks.

    Parameters:
        bookmarks_path: Optional override path to Edge Bookmarks JSON

    Returns:
        dict: {status, count, bookmarks}
    """
    path = _find_first_existing(EDGE_BOOKMARK_PATHS) if not bookmarks_path else Path(bookmarks_path)
    return read_chromium_bookmarks(path)


async def add_edge_bookmark(
    title: str,
    url: str,
    folder: str | None = None,
    bookmarks_path: str | None = None,
) -> dict[str, Any]:
    """Add a bookmark to Edge Bookmarks JSON.

    Parameters:
        title: Bookmark title
        url: Bookmark URL
        folder: Optional target folder name
        bookmarks_path: Optional override path

    Returns:
        dict: {status, ...}
    """
    path = _find_first_existing(EDGE_BOOKMARK_PATHS) if not bookmarks_path else Path(bookmarks_path)
    return write_chromium_bookmark(path, title, url, folder)


async def edit_edge_bookmark(
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
    """Edit an Edge bookmark by id or url (rename/move).
    """
    path = _find_first_existing(EDGE_BOOKMARK_PATHS) if not bookmarks_path else Path(bookmarks_path)
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


async def delete_edge_bookmark(
    *,
    id: str | None = None,
    url: str | None = None,
    dry_run: bool = False,
    bookmarks_path: str | None = None,
) -> dict[str, Any]:
    """Delete an Edge bookmark by id or url.
    """
    path = _find_first_existing(EDGE_BOOKMARK_PATHS) if not bookmarks_path else Path(bookmarks_path)
    return delete_chromium_bookmark(path, id=id, url=url, dry_run=dry_run)


# Register MCP tools without shadowing callables
LIST_EDGE_BOOKMARKS_TOOL = mcp.tool(name="list_edge_bookmarks")(list_edge_bookmarks)
ADD_EDGE_BOOKMARK_TOOL = mcp.tool(name="add_edge_bookmark")(add_edge_bookmark)
EDIT_EDGE_BOOKMARK_TOOL = mcp.tool(name="edit_edge_bookmark")(edit_edge_bookmark)
DELETE_EDGE_BOOKMARK_TOOL = mcp.tool(name="delete_edge_bookmark")(delete_edge_bookmark)
