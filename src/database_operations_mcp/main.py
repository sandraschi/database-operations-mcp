"""
Main module for Database Operations MCP.

This module provides the main entry point for the Database Operations MCP server,
which supports both stdio and HTTP transports with FastMCP 2.12.4.
"""

import asyncio
import logging
import os
import signal
import sys
from typing import Literal

# Import our centralized MCP configuration
from .config.mcp_config import get_mcp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


class DatabaseOperationsMCP:
    """Main MCP server class for database operations."""

    def __init__(self) -> None:
        """Initialize the MCP server."""
        # Use the global MCP instance
        self.mcp = get_mcp()
        self._shutdown_event = asyncio.Event()

        # Import all tool modules to ensure @mcp.tool decorators are executed
        self._import_all_tools()

    async def _register_handlers(self) -> None:
        """Import all handler modules to register tools via decorators.

        In FastMCP 2.11.3, tools are registered using the @mcp.tool() decorator
        when modules are imported. This function ensures all handler modules
        are imported to trigger the decorators.
        """
        # Import all handler modules to register their tools via decorators

        # Log that tools have been registered
        logger.info("All tool handlers imported and registered via decorators")

    async def _shutdown(self, signal: signal.Signals | None = None) -> None:
        """Handle server shutdown."""
        if signal:
            logger.info(f"Received exit signal {signal.name}...")

        logger.info("Shutting down Database Operations MCP server...")
        self._shutdown_event.set()

        if self.mcp and self._loop:
            logger.info("Cleaning up MCP resources...")
            # Cancel all running tasks
            tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            self._loop.stop()

    def _register_signal_handlers(self) -> None:
        """Register signal handlers for graceful shutdown."""
        if sys.platform == "win32":
            # Windows signal handling
            signal.signal(signal.SIGINT, lambda s, f: asyncio.create_task(self._shutdown()))
            signal.signal(signal.SIGTERM, lambda s, f: asyncio.create_task(self._shutdown()))

    def _import_all_tools(self) -> None:
        """Import portmanteau tools from tools/ directory to register them."""
        try:
            # Import all portmanteau tools from tools/ directory
            # These imports trigger @mcp.tool() decorators
            from .tools import (  # noqa: F401
                browser_bookmarks,
                chrome_bookmarks,
                chrome_profiles,
                db_analysis,
                db_connection,
                db_fts,
                db_management,
                db_operations,
                db_operations_extended,
                db_schema,
                firefox_backup,
                firefox_bookmarks,
                firefox_curated,
                firefox_profiles,
                firefox_tagging,
                firefox_utils,
                help_system,
                media_library,
                sync_tools,
                system_init,
                windows_system,
            )

            logger.info("All 21 portmanteau tools imported successfully!")

        except ImportError as e:
            logger.error(f"Failed to import tool modules: {e}")
            raise

    def _import_handlers(self) -> None:
        """Import handler modules to trigger @mcp.tool decorators."""
        # All imports are done in __init__ to trigger decorators
        # This method is kept for backward compatibility
        from fastmcp.utilities.inspect import get_tools

        tools = get_tools(self.mcp)
        logger.info(f"Registered {len(tools)} tools with FastMCP")

    def _detect_transport(self) -> Literal["stdio", "http", "dual"]:
        """Detect which transport to use based on environment variables or command line args.

        Returns:
            str: Transport type ("stdio", "http", or "dual")
        """
        # Check environment variable first
        transport = os.getenv("MCP_TRANSPORT", "").lower()

        # Check command line arguments
        if "--dual" in sys.argv or "--both" in sys.argv:
            transport = "dual"
        elif "--http" in sys.argv:
            transport = "http"
        elif "--stdio" in sys.argv:
            transport = "stdio"

        # Default to dual interface for maximum compatibility
        if transport not in ["stdio", "http", "dual"]:
            transport = "dual"

        logger.info(f"Detected transport: {transport}")
        return transport

    async def _run_http_server(self) -> int:
        """Run the MCP server using HTTP transport.

        Returns:
            int: Exit code (0 for success, non-zero for error)
        """
        try:
            logger.info("Starting Database Operations MCP Server (HTTP transport)...")

            # Log MCP configuration
            logger.info(f"MCP Name: {self.mcp.name}")
            logger.info(f"MCP Version: {self.mcp.version}")

            # Get HTTP configuration from environment
            host = os.getenv("MCP_HOST", "0.0.0.0")
            port = int(os.getenv("MCP_PORT", "8000"))

            logger.info(f"HTTP server will bind to {host}:{port}")

            # Register signal handlers for graceful shutdown
            self._register_signal_handlers()

            # Run the HTTP server
            logger.info("Starting HTTP server...")
            await self.mcp.run_http_async(host=host, port=port, show_banner=True)

            return 0

        except Exception as e:
            logger.error(f"Error running HTTP server: {e}", exc_info=True)
            return 1

    async def _run_stdio_server(self) -> int:
        """Run the MCP server using stdio transport.

        Returns:
            int: Exit code (0 for success, non-zero for error)
        """
        try:
            logger.info("Starting Database Operations MCP Server (stdio transport)...")

            # Log MCP configuration
            logger.info(f"MCP Name: {self.mcp.name}")
            logger.info(f"MCP Version: {self.mcp.version}")

            # Register signal handlers for graceful shutdown
            self._register_signal_handlers()

            # Run the stdio server
            logger.info("Starting stdio server...")
            await self.mcp.run_stdio_async()

            return 0

        except Exception as e:
            logger.error(f"Error running stdio server: {e}", exc_info=True)
            return 1

    async def _run_dual_servers(self) -> int:
        """Run both stdio and HTTP servers concurrently.

        Returns:
            int: Exit code (0 for success, non-zero for error)
        """
        try:
            logger.info("Starting Database Operations MCP Server (dual interface)...")
            logger.info("Running both stdio and HTTP transports concurrently")

            # Get HTTP configuration
            host = os.getenv("MCP_HOST", "0.0.0.0")
            port = int(os.getenv("MCP_PORT", "8000"))
            logger.info(f"HTTP server will bind to {host}:{port}")

            # Create tasks for both servers
            stdio_task = asyncio.create_task(self._run_stdio_server())
            http_task = asyncio.create_task(self._run_http_server())

            # Register signal handlers for graceful shutdown
            self._register_signal_handlers()

            # Wait for either server to finish (they shouldn't finish normally)
            done, pending = await asyncio.wait(
                [stdio_task, http_task], return_when=asyncio.FIRST_COMPLETED
            )

            # Cancel remaining tasks
            for task in pending:
                task.cancel()

            # Wait for tasks to finish
            await asyncio.gather(*pending, return_exceptions=True)

            # Return the result of the first completed task
            for task in done:
                try:
                    return task.result()
                except Exception as e:
                    logger.error(f"Task failed: {e}")
                    return 1

            return 0

        except Exception as e:
            logger.error(f"Error running dual servers: {e}", exc_info=True)
            return 1

    async def _run_async(self) -> int:
        """Async entry point for the MCP server (not used in current implementation).

        Returns:
            int: Exit code (0 for success, non-zero for error)
        """
        # This method is kept for backward compatibility but is not used
        # as FastMCP manages its own event loop
        return 0

    def run(self) -> int:
        """Run the MCP server.

        Returns:
            int: Exit code (0 for success, non-zero for error)
        """
        try:
            # Configure logging for FastMCP
            import logging

            logging.basicConfig(
                level=logging.DEBUG,  # Set default log level to DEBUG
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                stream=sys.stderr,
            )

            # Detect which transport to use
            transport = self._detect_transport()

            if transport == "http":
                # Run HTTP server asynchronously
                logger.info("Running HTTP server...")
                return asyncio.run(self._run_http_server())
            elif transport == "dual":
                # Run both servers concurrently
                logger.info("Running dual interface (stdio + HTTP)...")
                return asyncio.run(self._run_dual_servers())
            else:
                # Run stdio server (backward compatibility)
                logger.info("Running stdio server...")

                # Register signal handlers for graceful shutdown
                self._register_signal_handlers()

                # Run the FastMCP server
                logger.info("Starting Database Operations MCP Server...")

                # Log MCP configuration
                logger.info(f"MCP Name: {self.mcp.name}")
                logger.info(f"MCP Version: {self.mcp.version}")

                # Run the server
                logger.info("Calling mcp.run()...")
                self.mcp.run()

                return 0

        except Exception as e:
            logger.error(f"Error running MCP server: {e}", exc_info=True)
            return 1


def main() -> int:
    """Entry point for the MCP server.

    Command line options:
        --stdio: Force stdio transport (default for backward compatibility)
        --http: Run HTTP server only
        --dual: Run both stdio and HTTP servers concurrently (default)

    Environment variables:
        MCP_TRANSPORT: Set transport type (stdio, http, dual)
        MCP_HOST: HTTP server host (default: 0.0.0.0)
        MCP_PORT: HTTP server port (default: 8000)
    """
    # Configure basic logging first
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )

    logger = logging.getLogger(__name__)

    # Show transport options if requested
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Database Operations MCP Server")
        print("Supports stdio, HTTP, and dual interface modes")
        print()
        print("Usage:")
        print("  python -m database_operations_mcp.main [--stdio|--http|--dual]")
        print()
        print("Options:")
        print("  --stdio    Run with stdio transport only")
        print("  --http     Run with HTTP transport only")
        print("  --dual     Run both stdio and HTTP transports (default)")
        print("  --help     Show this help message")
        print()
        print("Environment Variables:")
        print("  MCP_TRANSPORT    Transport type (stdio, http, dual)")
        print("  MCP_HOST         HTTP server host (default: 0.0.0.0)")
        print("  MCP_PORT         HTTP server port (default: 8000)")
        return 0

    logger.info("Starting Database Operations MCP Server...")

    try:
        # Create the server instance
        logger.info("Initializing DatabaseOperationsMCP...")
        server = DatabaseOperationsMCP()
        logger.info("DatabaseOperationsMCP initialized successfully")

        # Run the server
        logger.info("Starting server...")
        return server.run()

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
