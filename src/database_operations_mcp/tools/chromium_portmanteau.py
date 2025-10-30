from pathlib import Path
from typing import Any

from database_operations_mcp.config.mcp_config import mcp

from .chromium_common import (
    CHROME_BOOKMARK_PATHS,
    EDGE_BOOKMARK_PATHS,
    BRAVE_BOOKMARK_PATHS,
    _find_first_existing,
    read_chromium_bookmarks,
    write_chromium_bookmark,
    edit_chromium_bookmark,
    delete_chromium_bookmark,
)


def _paths_for(browser: str) -> list[str]:
    b = browser.lower()
    if b == "chrome":
        return CHROME_BOOKMARK_PATHS
    if b == "edge":
        return EDGE_BOOKMARK_PATHS
    if b == "brave":
        return BRAVE_BOOKMARK_PATHS
    raise ValueError(f"Unsupported Chromium browser: {browser}")


@mcp.tool()
async def chromium_bookmarks(
    operation: str,
    browser: str,
    # list
    bookmarks_path: str | None = None,
    limit: int = 1000,
    # add
    title: str | None = None,
    url: str | None = None,
    folder: str | None = None,
    allow_duplicates: bool = False,
    # edit
    id: str | None = None,
    new_title: str | None = None,
    new_folder: str | None = None,
    create_folders: bool = True,
    dry_run: bool = False,
    # delete
) -> dict[str, Any]:
    """Chromium bookmarks portmanteau (Chrome/Edge/Brave): list/add/edit/delete.

    Parameters:
        operation: One of 'list', 'add', 'edit', 'delete'
        browser: 'chrome' | 'edge' | 'brave'
        bookmarks_path: Optional JSON path override (env vars supported)

        list:
          - limit: max items to include in response

        add:
          - title, url (required), folder (optional), allow_duplicates

        edit:
          - id or url (one required), new_title/new_folder, create_folders, dry_run

        delete:
          - id or url (one required), dry_run

    Returns:
        dict with status and operation-specific data or descriptive error.
    """
    try:
        path: Path | None
        if bookmarks_path:
            path = Path(bookmarks_path)
        else:
            path = _find_first_existing(_paths_for(browser))

        op = operation.lower()
        if op == "list":
            res = read_chromium_bookmarks(path)
            if res.get("status") == "success":
                if isinstance(limit, int) and limit > 0:
                    res["bookmarks"] = res.get("bookmarks", [])[:limit]
            return res

        if op == "add":
            if not url:
                return {"status": "error", "message": "url is required for add"}
            return write_chromium_bookmark(path, title or url, url, folder, allow_duplicates)

        if op == "edit":
            if id is None and url is None:
                return {"status": "error", "message": "id or url is required for edit"}
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

        if op == "delete":
            if id is None and url is None:
                return {"status": "error", "message": "id or url is required for delete"}
            return delete_chromium_bookmark(path, id=id, url=url, dry_run=dry_run)

        return {"status": "error", "message": f"Unsupported operation: {operation}"}
    except PermissionError as e:
        return {"status": "error", "message": f"Failed due to permission error: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"Operation failed: {e}"}
