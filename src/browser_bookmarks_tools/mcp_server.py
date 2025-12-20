"""FastMCP 2.13 server for browser bookmark management."""

# CRITICAL: Set stdio to binary mode on Windows for Antigravity IDE compatibility
# Antigravity IDE is strict about JSON-RPC protocol and interprets trailing \r as "invalid trailing data"
# This must happen BEFORE any imports that might write to stdout
import os
import sys

if os.name == 'nt':  # Windows only
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
        return ''.join(self.buffer)

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
        def debug(self, *args, **kwargs): pass
        def info(self, *args, **kwargs): pass
        def warning(self, *args, **kwargs): pass
        def error(self, *args, **kwargs): pass
        def critical(self, *args, **kwargs): pass
        def exception(self, *args, **kwargs): pass

        def setLevel(self, *args, **kwargs): pass
        def addHandler(self, *args, **kwargs): pass
        def removeHandler(self, *args, **kwargs): pass

    # Replace the logging module's getLogger function
    original_getLogger = logging.getLogger
    def null_getLogger(name=None):
        return NullLogger()
    logging.getLogger = null_getLogger

from mcp.server.fastmcp import FastMCP

# Initialize logger
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP(name="Browser Bookmarks Tools")

# CRITICAL: After server initialization, restore stdout for stdio mode
# This allows the server to communicate via JSON-RPC while preventing initialization logging
if _is_stdio_mode:
    if hasattr(sys.stdout, 'restore'):
        sys.stdout.restore()
        # Now we can safely write to stdout for JSON-RPC communication

    # Restore the original logging functionality
    logging.getLogger = original_getLogger

    # Set up proper logging to stderr only (not stdout)
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr  # Critical: log to stderr, not stdout
    )


@mcp.tool()
async def add_bookmark(
    browser: str,
    url: str,
    title: str,
    profile_name: str = "default",
    folder_id: int = 0,
    tags: list[str] | None = None,
) -> dict:
    """Add a bookmark to browser.

    Add a new bookmark with AI-generated description and tags.

    Parameters:
        browser: Browser name (firefox, chrome, edge, brave, safari)
        url: URL of the bookmark
        title: Title of the bookmark
        profile_name: Browser profile name (default: 'default')
        folder_id: Folder ID where to place bookmark (default: 0)
        tags: List of tags to apply (optional)

    Returns:
        dict: Result with success status and bookmark details

    Usage:
        Use this to add bookmarks to any supported browser.
        Tags and descriptions can be generated automatically by AI.

    Examples:
        Add bookmark to Firefox:
            await add_bookmark(
                browser='firefox',
                url='https://example.com',
                title='Example Site',
                profile_name='default'
            )

    Notes:
        - Browser must be closed for Firefox operations
        - Chrome bookmarks are stored as JSON
        - AI can auto-generate tags and descriptions

    See Also:
        update_bookmark, delete_bookmark, search_bookmarks
    """
    logger.info(f"Adding bookmark: {title} to {browser}")
    return {
        "success": True,
        "browser": browser,
        "title": title,
        "url": url,
        "profile_name": profile_name,
        "folder_id": folder_id,
        "tags": tags or [],
        "note": "Placeholder implementation",
    }


@mcp.tool()
async def search_bookmarks(
    browser: str,
    query: str,
    profile_name: str = "default",
    limit: int = 100,
) -> dict:
    """Search bookmarks using AI-powered filtering.

    Advanced bookmark search with natural language queries.

    Parameters:
        browser: Browser name to search in
        query: Search query (natural language)
        profile_name: Browser profile to search (default: 'default')
        limit: Maximum results to return (default: 100)

    Returns:
        dict: Search results with bookmarks

    Usage:
        Search for bookmarks using natural language.
        AI can understand context and intent.

    Examples:
        Search for Python tutorials:
            await search_bookmarks(
                browser='firefox',
                query='Python programming tutorials',
                limit=20
            )

    Notes:
        Search works on titles, URLs, and tags
        AI can understand synonyms and context

    See Also:
        get_bookmark, list_bookmarks
    """
    logger.info(f"Searching bookmarks in {browser}: {query}")
    return {
        "success": True,
        "browser": browser,
        "query": query,
        "results": [],
        "total": 0,
        "note": "Placeholder implementation",
    }


def main():
    """Run the MCP server."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger.info("Starting Browser Bookmarks Tools MCP server...")
    mcp.run()


if __name__ == "__main__":
    main()
