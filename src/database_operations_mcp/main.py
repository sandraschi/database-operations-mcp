"""
Main module for Database Operations MCP.

This module provides the main entry point for the Database Operations MCP server,
which communicates via stdio with the FastMCP 2.10.1 client.
"""
import asyncio
import logging
import signal
import sys
import platform
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
            
        # Import and register all tools from the handlers package
        from .handlers import register_all_tools
        register_all_tools(self.mcp)
        # All tools are registered via register_all_tools
    
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
    
    def run(self) -> int:
        """Run the MCP server.
        
        Returns:
            int: Exit code (0 for success, non-zero for error)
        """
        exit_code = 0
        
        try:
            # Register signal handlers for graceful shutdown
            self._register_signal_handlers()
            
            # Create the MCP server
            self.mcp = FastMCP(
                "database-operations-mcp",
                "Database Operations MCP Server",
                version="0.1.0"
            )
            
            # Register all tool handlers
            import asyncio
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._register_handlers())
            
            # Run the MCP server
            self.mcp.run()
            
        except asyncio.CancelledError:
            logger.info("Server task was cancelled")
            exit_code = 1
        except Exception as e:
            logger.critical(f"Fatal error: {str(e)}", exc_info=True)
            exit_code = 1
        finally:
            logger.info("Database Operations MCP server stopped")
            
        return exit_code

def main():
    """Entry point for the MCP server."""
    # Create the server instance
    server = DatabaseOperationsMCP()
    
    # Run the server (synchronously)
    try:
        return server.run()
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
        return 0
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    main()
