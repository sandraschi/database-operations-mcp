import json
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
    """Chromium bookmarks portmanteau (Chrome/Edge/Brave): unified CRUD operations.

    This tool provides a single interface for all bookmark operations across Chromium-based
    browsers (Chrome, Edge, Brave). Use this instead of individual browser tools for
    consistent API and operation discovery.

    Prerequisites:
        - Target browser must be installed
        - Bookmarks file must exist at default location (unless bookmarks_path provided)
        - Write permissions required for add/edit/delete operations

    Parameters:
        operation (str, REQUIRED): The operation to perform. Valid values:
            - 'list': List bookmarks with optional limit
            - 'add': Add a new bookmark
            - 'edit': Edit existing bookmark (rename/move)
            - 'delete': Delete a bookmark

        browser (str, REQUIRED): Target browser. Valid values: 'chrome', 'edge', 'brave'
            Case-insensitive. Must match installed browser.

        bookmarks_path (str, OPTIONAL): Override default Bookmarks JSON path
            Format: Full path or environment variable (e.g., '%LOCALAPPDATA%\\...')
            Default: Auto-detected from browser type
            Use when: Testing with alternate bookmark files or custom locations

        limit (int, OPTIONAL, for 'list'): Maximum bookmarks to return
            Range: 1-10000
            Default: 1000
            Performance: Lower values improve response time for large collections

        # Parameters for 'add' operation:
        title (str, REQUIRED for 'add'): Bookmark display title
            Format: Plain text, max 255 characters
            Example: "Python Documentation"
            Note: If empty, URL will be used as title

        url (str, REQUIRED for 'add'): Bookmark URL
            Format: Full URL including protocol (e.g., 'https://example.com')
            Validation: Must start with http:// or https://
            Example: "https://docs.python.org/3/"

        folder (str, OPTIONAL for 'add'): Target folder name or path
            Format: Folder name (e.g., "Reading") or nested path (e.g., "Reading/Tech")
            Default: Browser's "Other Bookmarks" folder
            Note: Folders created automatically if create_folders=True (edit only)

        allow_duplicates (bool, OPTIONAL): Allow duplicate URLs
            Default: False (duplicates skipped silently)
            Use when: Intentionally adding same URL multiple times

        # Parameters for 'edit' and 'delete' operations:
        id (str, OPTIONAL): Bookmark ID from list operation
            Format: String representation of numeric ID
            Example: "12345"
            Note: Either 'id' or 'url' required for edit/delete

        url (str, OPTIONAL for 'edit'/'delete'): Bookmark URL to identify target
            Format: Full URL matching existing bookmark
            Use when: You have URL but not ID (requires exact match)

        new_title (str, OPTIONAL for 'edit'): New display title
            Format: Plain text, max 255 characters
            Example: "Updated Bookmark Title"

        new_folder (str, OPTIONAL for 'edit'): Move bookmark to this folder
            Format: Folder name or nested path (e.g., "Reading/Docs")
            Behavior: Creates folder path if create_folders=True

        create_folders (bool, OPTIONAL for 'edit'): Auto-create missing folders
            Default: True
            Use False when: Folder must exist (prevents typos)

        dry_run (bool, OPTIONAL for 'edit'/'delete'): Preview without changes
            Default: False
            Use True when: Testing operations or verifying before commit

    Returns:
        dict: Operation result with structured status

        Success Response Structure:
        {
            "status": "success",
            "operation": str,          # Echo of operation performed
            "browser": str,           # Browser used
            # For 'list':
            "count": int,             # Total bookmarks found
            "bookmarks": [            # List of bookmark objects
                {
                    "title": str,     # Display title
                    "url": str,       # Full URL
                    "parent": str      # Parent folder name (if any)
                }
            ],
            # For 'add':
            "bookmark": {             # Created bookmark details
                "title": str,
                "url": str
            },
            # For 'edit':
            "bookmark": {             # Updated bookmark details
                "id": str,
                "title": str,
                "url": str
            },
            # For 'delete':
            "deleted": bool         # Confirmation
        }

        Error Response Structure:
        {
            "status": "error",
            "error": str,             # Human-readable error message
            "error_code": str,        # Machine-readable error code
            "suggestion": str,        # How to fix the error
            "operation": str,         # Operation that failed
            "browser": str            # Browser that failed
        }

    Common Issues & Solutions:

        1. "Unsupported Chromium browser: {browser}"
           CAUSE: Browser parameter doesn't match 'chrome', 'edge', or 'brave'
           FIX: Use lowercase: 'chrome', 'edge', or 'brave'
           Example: browser="Chrome" → browser="chrome"

        2. "Bookmarks file not found"
           CAUSE: Browser not installed or bookmarks file missing
           FIX:
           - Verify browser is installed
           - Check default paths exist: %LOCALAPPDATA%\\[Browser]\\User Data\\Default\\Bookmarks
           - Provide explicit bookmarks_path if using custom location
           WORKAROUND: Use bookmarks_path to point to existing JSON file

        3. "Failed due to permission error: ..."
           CAUSE: File is read-only or browser is open with file locked
           FIX:
           - Close the browser completely (check task manager for background processes)
           - Verify file permissions (Windows: Properties → Security)
           - Run with elevated permissions if needed
           WORKAROUND: Copy Bookmarks file to writable location, edit, copy back

        4. "url is required for add" / "id or url is required for edit"
           CAUSE: Missing required identifier parameter
           FIX:
           - For 'add': Always provide 'url' parameter
           - For 'edit'/'delete': Provide either 'id' (from list) or 'url' (exact match)

        5. "Unsupported operation: {operation}"
           CAUSE: Operation parameter doesn't match valid values
           FIX: Use one of: 'list', 'add', 'edit', 'delete'
           Valid operations:
           - 'list': Retrieve bookmarks
           - 'add': Create new bookmark
           - 'edit': Modify existing bookmark
           - 'delete': Remove bookmark

        6. "Operation failed: ..."
           CAUSE: Unexpected error (malformed JSON, disk full, etc.)
           FIX:
           - Check error message for specific cause
           - Verify Bookmarks file is valid JSON (try opening in text editor)
           - Check disk space
           - Review system logs for additional details

    Examples:

        # Example 1: List first 50 Edge bookmarks (most common)
        result = await chromium_bookmarks(
            operation="list",
            browser="edge",
            limit=50
        )
        # Returns: {"status": "success", "count": 150, "bookmarks": [...]}
        # Use when: Browsing or searching bookmark collection

        # Example 2: Add bookmark to Chrome in specific folder
        result = await chromium_bookmarks(
            operation="add",
            browser="chrome",
            title="Python 3.12 Docs",
            url="https://docs.python.org/3.12/",
            folder="Programming/Docs"
        )
        # Returns: {"status": "success", "bookmark": {"title": "...", "url": "..."}}
        # Use when: Saving new bookmark with organization

        # Example 3: Rename bookmark by URL (dry run first)
        result = await chromium_bookmarks(
            operation="edit",
            browser="brave",
            url="https://example.com/docs",
            new_title="Updated Docs Title",
            dry_run=True
        )
        # Returns: {"status": "planned", "action": "edit", "edited": True, "moved": False}
        # Use when: Previewing changes before applying

        # Example 4: Delete bookmark by ID
        result = await chromium_bookmarks(
            operation="delete",
            browser="edge",
            id="12345",
            dry_run=False
        )
        # Returns: {"status": "success", "deleted": True}
        # Use when: Removing unwanted bookmark

        # Example 5: Error handling pattern
        result = await chromium_bookmarks(operation="add", browser="chrome", url="https://example.com")
        if result.get("status") == "error":
            print(f"Error: {result.get('error')}")
            print(f"Fix: {result.get('suggestion')}")
            # AI can now provide helpful guidance to user

    Platform Notes:
        - Windows paths use backslashes in environment variables
        - Bookmarks file locked while browser is running (close browser for writes)
        - Folder paths use forward slashes: "Reading/Tech" not "Reading\\Tech"
    """
    try:
        path: Path | None
        if bookmarks_path:
            path = Path(bookmarks_path)
        else:
            path = _find_first_existing(_paths_for(browser))

        op = operation.lower()

        # Validate browser
        if browser.lower() not in ("chrome", "edge", "brave"):
            return {
                "status": "error",
                "error_code": "CHROMIUM_INVALID_BROWSER",
                "error": f"browser={browser} not in [chrome,edge,brave]",
                "context": {
                    "provided": browser,
                    "valid": ["chrome", "edge", "brave"],
                    "operation": operation,
                },
                "fix": "set browser to one of: chrome|edge|brave",
            }

        # Validate path exists
        if path is None or not path.exists():
            expected_paths = _paths_for(browser)
            return {
                "status": "error",
                "error_code": "CHROMIUM_FILE_NOT_FOUND",
                "error": f"bookmarks_file missing: {path}",
                "context": {
                    "browser": browser,
                    "attempted_path": str(path) if path else None,
                    "expected_paths": expected_paths,
                    "operation": operation,
                },
                "fix": f"verify {browser} installed | set bookmarks_path to existing file",
            }

        if op == "list":
            res = read_chromium_bookmarks(path)
            if res.get("status") == "success":
                if isinstance(limit, int) and limit > 0:
                    res["bookmarks"] = res.get("bookmarks", [])[:limit]
            return res

        if op == "add":
            if not url:
                return {
                    "status": "error",
                    "error_code": "CHROMIUM_MISSING_URL",
                    "error": "operation=add requires url parameter",
                    "context": {
                        "operation": operation,
                        "browser": browser,
                        "missing_required": ["url"],
                        "provided_params": {"title": title, "folder": folder},
                    },
                    "fix": "set url parameter with full URL (e.g., 'https://example.com')",
                }
            return write_chromium_bookmark(path, title or url, url, folder, allow_duplicates)

        if op == "edit":
            if id is None and url is None:
                return {
                    "status": "error",
                    "error_code": "CHROMIUM_MISSING_IDENTIFIER",
                    "error": "operation=edit requires id OR url parameter",
                    "context": {
                        "operation": operation,
                        "browser": browser,
                        "missing": {"id": id, "url": url},
                    },
                    "fix": "set id=<bookmark_id> OR url=<exact_url> to identify bookmark",
                }
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
                return {
                    "status": "error",
                    "error_code": "CHROMIUM_MISSING_IDENTIFIER",
                    "error": "operation=delete requires id OR url parameter",
                    "context": {
                        "operation": operation,
                        "browser": browser,
                        "missing": {"id": id, "url": url},
                    },
                    "fix": "set id=<bookmark_id> OR url=<exact_url> to identify bookmark",
                }
            return delete_chromium_bookmark(path, id=id, url=url, dry_run=dry_run)

        return {
            "status": "error",
            "error_code": "CHROMIUM_INVALID_OPERATION",
            "error": f"operation={operation} not in [list,add,edit,delete]",
            "context": {
                "provided": operation,
                "valid": ["list", "add", "edit", "delete"],
                "browser": browser,
            },
            "fix": "set operation to one of: list|add|edit|delete",
        }
    except PermissionError as e:
        return {
            "status": "error",
            "error_code": "CHROMIUM_PERMISSION_DENIED",
            "error": f"permission_denied: {str(e)}",
            "context": {
                "file_path": str(path),
                "browser": browser,
                "operation": operation,
                "exception": type(e).__name__,
            },
            "fix": f"close {browser} completely | check file permissions | run elevated",
        }
    except ValueError as e:
        return {
            "status": "error",
            "error_code": "CHROMIUM_INVALID_INPUT",
            "error": f"invalid_input: {str(e)}",
            "context": {
                "exception": type(e).__name__,
                "details": str(e),
                "operation": operation,
                "browser": browser,
            },
            "fix": "verify parameter formats match expected types",
        }
    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "error_code": "CHROMIUM_INVALID_JSON",
            "error": f"json_decode_failed: {str(e)}",
            "context": {
                "file_path": str(path),
                "line": getattr(e, "lineno", None),
                "column": getattr(e, "colno", None),
                "exception": type(e).__name__,
                "operation": operation,
            },
            "fix": "validate JSON syntax | check file corruption | restore from backup",
        }
    except Exception as e:
        import traceback

        tb_lines = traceback.format_exc().splitlines()
        return {
            "status": "error",
            "error_code": "CHROMIUM_UNEXPECTED_ERROR",
            "error": f"unexpected_error: {type(e).__name__}: {str(e)}",
            "context": {
                "exception": type(e).__name__,
                "file_path": str(path) if path else None,
                "browser": browser,
                "operation": operation,
                "traceback": tb_lines[-3:] if tb_lines else None,  # Last 3 lines
            },
            "fix": "check disk space | validate file integrity | review traceback",
        }
