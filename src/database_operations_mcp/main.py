"""
Main module for Database Operations MCP.

This module provides the main entry point for the Database Operations MCP server,
which communicates via stdio with the FastMCP 2.10.1 client.
"""
import sys
import logging
import signal
import asyncio
from typing import Optional, List, Dict, Any
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

class DatabaseOperationsMCP:
    """Main application class for Database Operations MCP server."""
    
    def __init__(self) -> None:
        """Initialize the MCP server."""
        self.mcp: Optional[FastMCP] = None
        self._shutdown_event = asyncio.Event()
        
    async def _register_handlers(self) -> None:
        """Register all tool handlers with the MCP server."""
        if not self.mcp:
            return
            
        # Import handler modules
        from .handlers import (
            connection_tools,
            data_tools,
            query_tools,
            schema_tools,
            management_tools,
            fts_tools,
            registry_tools,
            windows_tools,
            calibre_tools,
            media_tools,
            init_tools,
            help_tools
        )
        
        # Register all tool modules
        handlers = [
            connection_tools,
            data_tools,
            query_tools,
            schema_tools,
            management_tools,
            fts_tools,
            registry_tools,
            windows_tools,
            calibre_tools,
            media_tools,
            init_tools,
            help_tools
        ]
        
        for handler in handlers:
            try:
                handler.register_tools(self.mcp)
                logger.debug(f"Successfully registered handler: {handler.__name__}")
            except Exception as e:
                logger.error(f"Failed to register handler {handler.__name__}: {str(e)}")
                raise
    
    async def _shutdown(self, signal: Optional[signal.Signals] = None) -> None:
        """Handle server shutdown."""
        if signal:
            logger.info(f"Received exit signal {signal.name}...")
        
        logger.info("Shutting down Database Operations MCP server...")
        self._shutdown_event.set()
        
        # Add any cleanup code here
        if self.mcp:
            logger.info("Cleaning up MCP resources...")
            # Cleanup any resources used by the MCP server
            
    def _register_signal_handlers(self) -> None:
        """Register signal handlers for graceful shutdown."""
        if sys.platform == 'win32':
            # Windows signal handling
            signal.signal(signal.SIGINT, lambda s, f: asyncio.create_task(self._shutdown()))
            signal.signal(signal.SIGTERM, lambda s, f: asyncio.create_task(self._shutdown()))
        else:
            # Unix signal handling
            loop = asyncio.get_running_loop()
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(
                    sig, 
                    lambda s=sig: asyncio.create_task(self._shutdown(s))
                )
    
    async def run(self) -> int:
        """Run the MCP server.
        
        Returns:
            int: Exit code (0 for success, non-zero for error)
        """
        exit_code = 0
        
        try:
            # Initialize MCP server
            self.mcp = FastMCP(
                name="database-operations-mcp",
                version="0.1.0",
                description="Database Operations MCP Server"
            )
            
            # Register signal handlers
            self._register_signal_handlers()
            
            # Register all tool handlers
            await self._register_handlers()
            
            # Configure logging to stderr for stdio transport
            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            
            # Get root logger and add handler
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.INFO)
            root_logger.addHandler(console_handler)
            
            logger.info("Database Operations MCP server starting with stdio transport...")
            
            # Run the server with stdio
            await self.mcp.run()
            
            # Log server start
            logger.info("MCP server is running and listening on stdio")
            
            # Keep the server running until shutdown is requested
            while not self._shutdown_event.is_set():
                try:
                    await asyncio.sleep(0.1)
                except asyncio.CancelledError:
                    break
            
        except asyncio.CancelledError:
            logger.info("Server task was cancelled")
            exit_code = 1
        except Exception as e:
            logger.critical(f"Fatal error: {str(e)}", exc_info=True)
            exit_code = 1
        finally:
            logger.info("Database Operations MCP server stopped")
            
        return exit_code

def main() -> int:
    """Main entry point for Database Operations MCP server.
    
    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    app = DatabaseOperationsMCP()
    return asyncio.run(app.run())

if __name__ == "__main__":
    main()
