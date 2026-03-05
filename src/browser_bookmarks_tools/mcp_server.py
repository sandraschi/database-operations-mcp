"""FastMCP 2.13 server for browser bookmark management."""

# CRITICAL: Set stdio to binary mode on Windows for Antigravity IDE compatibility
# Antigravity IDE is strict about JSON-RPC protocol and interprets trailing \r as "invalid trailing data"
# This must happen BEFORE any imports that might write to stdout
import os
import sys

if os.name == "nt":  # Windows only
    try:
        # Force binary mode for stdin/stdout to prevent CRLF conversion
        import msvcrt

        msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    except (OSError, AttributeError):
        # Fallback: just ensure no CRLF conversion
        pass


# DevNullStdout class for stdio mode to prevent any console output during initialization
class DevNullStdout:
    """Suppress all stdout writes during stdio mode to prevent JSON-RPC protocol corruption."""

    def __init__(self, original_stdout):
        self.original_stdout = original_stdout
        self.buffer = []

    def write(self, text):
        # Buffer output instead of writing to stdout
        self.buffer.append(text)

    def flush(self):
        # Do nothing - prevent any stdout writes
        pass

    def get_buffered_output(self):
        """Get all buffered output for debugging if needed."""
        return "".join(self.buffer)

    def restore(self):
        """Restore original stdout."""
        sys.stdout = self.original_stdout


# CRITICAL: Detect stdio mode BEFORE importing logger
# This must be done before ANY logging imports
_is_stdio_mode = not sys.stdout.isatty()

# NUCLEAR OPTION: Completely disable logger during stdio mode
# Import logger first, then replace it with a no-op to prevent any stdout writes
import logging

if _is_stdio_mode:
    # Replace stdout with our devnull version to catch any accidental writes
    original_stdout = sys.stdout
    sys.stdout = DevNullStdout(original_stdout)

    # Create a null logger that does nothing
    class NullLogger:
        def debug(self, *args, **kwargs):
            pass

        def info(self, *args, **kwargs):
            pass

        def warning(self, *args, **kwargs):
            pass

        def error(self, *args, **kwargs):
            pass

        def critical(self, *args, **kwargs):
            pass

        def exception(self, *args, **kwargs):
            pass

        def setLevel(self, *args, **kwargs):
            pass

        def addHandler(self, *args, **kwargs):
            pass

        def removeHandler(self, *args, **kwargs):
            pass

    # Replace the logging module's getLogger function
    original_getLogger = logging.getLogger

    def null_getLogger(name=None):
        return NullLogger()

    logging.getLogger = null_getLogger

from typing import Any
from mcp.server.fastmcp import FastMCP

# Initialize logger
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP(name="Browser Bookmarks Tools")

# ... (rest of the file logic continues correctly after the imports)

# CRITICAL: After server initialization, restore stdout for stdio mode
# This allows the server to communicate via JSON-RPC while preventing initialization logging
if _is_stdio_mode:
    if hasattr(sys.stdout, "restore"):
        sys.stdout.restore()
        # Now we can safely write to stdout for JSON-RPC communication

    # Restore the original logging functionality
    logging.getLogger = original_getLogger

    # Set up proper logging to stderr only (not stdout)
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,  # Critical: log to stderr, not stdout
    )


@mcp.tool()
async def browser_bookmarks(
    operation: str,
    browser: str,
    profile_name: str | None = None,
    # Core parameters
    folder_id: int | None = None,
    bookmark_id: str | None = None,
    url: str | None = None,
    title: str | None = None,
    folder: str | None = None,
    # Edit parameters
    new_title: str | None = None,
    new_folder: str | None = None,
    # Search/filter parameters
    tags: list[str] | None = None,
    search_query: str | None = None,
    search_type: str = "all",
    limit: int = 100,
    # Export parameters
    export_format: str = "json",
    export_path: str | None = None,
    # Advanced parameters
    batch_size: int = 100,
    similarity_threshold: float = 0.85,
    age_days: int = 365,
    check_links: bool = False,
    # Options
    allow_duplicates: bool = False,
    create_folders: bool = True,
    dry_run: bool = False,
    # Firefox lock bypass
    force_access: bool = False,
) -> dict[str, Any]:
    """Universal browser bookmark management portmanteau tool.

    Comprehensive cross-browser bookmark operations consolidating ALL bookmark
    management across supported browsers into a single interface. Automatically
    detects browser type and routes to appropriate browser-specific implementation.
    """
    from database_operations_mcp.tools.browser_bookmarks import (
        browser_bookmarks as real_impl,
    )

    return await real_impl(
        operation=operation,
        browser=browser,
        profile_name=profile_name,
        folder_id=folder_id,
        bookmark_id=bookmark_id,
        url=url,
        title=title,
        folder=folder,
        new_title=new_title,
        new_folder=new_folder,
        tags=tags,
        search_query=search_query,
        search_type=search_type,
        limit=limit,
        export_format=export_format,
        export_path=export_path,
        batch_size=batch_size,
        similarity_threshold=similarity_threshold,
        age_days=age_days,
        check_links=check_links,
        allow_duplicates=allow_duplicates,
        create_folders=create_folders,
        dry_run=dry_run,
        force_access=force_access,
    )


def main():
    """Run the MCP server."""
    from .transport import run_server as start_server

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )
    logger.info("Starting Browser Bookmarks Tools MCP server...")
    start_server(mcp, server_name="browser-bookmarks")


if __name__ == "__main__":
    main()
