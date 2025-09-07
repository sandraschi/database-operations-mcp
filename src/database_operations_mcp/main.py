"""
Main module for Database Operations MCP.

This module provides the main entry point for the Database Operations MCP server,
which communicates via stdio with the FastMCP 2.10.1 client.
"""
import asyncio
import logging
import signal
import sys
from typing import Any, Dict, Optional

# Import our centralized MCP configuration
from .config.mcp_config import get_mcp, mcp as global_mcp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
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
        from .tools import (
            connection_tools,
            query_tools,
            schema_tools,
            data_tools,
            fts_tools,
            management_tools,
            registry_tools,
            windows_tools,
            calibre_tools,
            media_tools,
            firefox,
            help_tools,
            init_tools,

            plex_tools
        )
        
    async def _register_handlers(self) -> None:
        """Import all handler modules to register tools via decorators.
        
        In FastMCP 2.11.3, tools are registered using the @mcp.tool() decorator
        when modules are imported. This function ensures all handler modules
        are imported to trigger the decorators.
        """
        # Import all handler modules to register their tools via decorators
        from . import handlers  # This will import all __init__.py imports
        
        # Log that tools have been registered
        logger.info("All tool handlers imported and registered via decorators")
    
    async def _shutdown(self, signal: Optional[signal.Signals] = None) -> None:
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
        if sys.platform == 'win32':
            # Windows signal handling
            signal.signal(signal.SIGINT, lambda s, f: asyncio.create_task(self._shutdown()))
            signal.signal(signal.SIGTERM, lambda s, f: asyncio.create_task(self._shutdown()))
    
    def _import_handlers(self) -> None:
        """Import handler modules to trigger @mcp.tool decorators."""
        # All imports are done in __init__ to trigger decorators
        # This method is kept for backward compatibility
        from fastmcp.utilities.inspect import get_tools
        tools = get_tools(self.mcp)
        logger.info(f"Registered {len(tools)} tools with FastMCP")
        
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
        exit_code = 0
        try:
            # Configure logging for FastMCP
            import logging
            logging.basicConfig(
                level=logging.DEBUG,  # Set default log level to DEBUG
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                stream=sys.stderr
            )
            
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
    """Entry point for the MCP server."""
    # Configure basic logging first
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Database Operations MCP Server...")
    
    try:
        # Create the server instance
        logger.info("Initializing DatabaseOperationsMCP...")
        server = DatabaseOperationsMCP()
        logger.info("DatabaseOperationsMCP initialized successfully")
        
        # Run the server (synchronously)
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
