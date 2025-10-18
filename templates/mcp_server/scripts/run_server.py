#!/usr/bin/env python3
"""
Run the MCP Server

This script starts the MCP server with proper configuration and error handling.
"""

import argparse
import asyncio
import logging
import os
import signal
import sys
from pathlib import Path

import uvicorn
from dotenv import load_dotenv

# Import MCP server after setting up logging and environment
from mcp_server.main import app, mcp

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging before importing other modules
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("mcp_server")

# Load environment variables from .env file
dotenv_path = project_root / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)


class MCPServer:
    """MCP Server wrapper with proper startup and shutdown handling."""

    def __init__(self, host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
        self.host = os.getenv("HOST", host)
        self.port = int(os.getenv("PORT", port))
        self.debug = os.getenv("DEBUG", str(debug)).lower() in ("true", "1", "t")
        self.server = None

        # Configure logging level
        log_level = os.getenv("LOG_LEVEL", "DEBUG" if self.debug else "INFO")
        logging.getLogger().setLevel(log_level)

        # Set up signal handlers
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)

    async def startup(self):
        """Perform startup tasks."""
        logger.info("Starting MCP Server...")

        # Register tools
        await self.register_tools()

        # Log startup information
        logger.info(f"MCP Server starting on http://{self.host}:{self.port}")
        logger.info(f"Debug mode: {'ON' if self.debug else 'OFF'}")
        logger.info(f"Python version: {sys.version.split()[0]}")
        logger.info(f"Environment: {os.getenv('ENV', 'development')}")

    async def register_tools(self):
        """Register all available tools."""
        try:
            # Import the tool registry
            from mcp_server.tool_registry import TOOL_REGISTRY

            # Register each tool
            for name, tool_func in TOOL_REGISTRY.items():
                if hasattr(tool_func, "name"):
                    mcp.register_tool(tool_func)
                    logger.debug(f"Registered tool: {name}")

            logger.info(f"Registered {len(TOOL_REGISTRY)} tools")

        except ImportError as e:
            logger.error(f"Failed to import tool registry: {e}")
            logger.warning("No tools registered. Did you run register_tools.py?")
        except Exception as e:
            logger.error(f"Error registering tools: {e}")

    async def shutdown(self):
        """Perform shutdown tasks."""
        logger.info("Shutting down MCP Server...")

        # Perform any necessary cleanup
        if hasattr(mcp, "shutdown"):
            await mcp.shutdown()

        logger.info("MCP Server shutdown complete")

    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        if self.server:
            self.server.should_exit = True

    async def run(self):
        """Run the MCP server."""
        # Perform startup tasks
        await self.startup()

        # Configure Uvicorn
        config = uvicorn.Config(
            app,
            host=self.host,
            port=self.port,
            log_level=logging.getLevelName(logger.getEffectiveLevel()).lower(),
            reload=self.debug,
            reload_dirs=[str(project_root / "src")] if self.debug else None,
            workers=1,  # MCP doesn't support multiple workers with in-memory state
        )

        # Create and run the server
        server = uvicorn.Server(config)
        self.server = server

        try:
            await server.serve()
        except asyncio.CancelledError:
            logger.info("Server shutdown requested")
        except Exception as e:
            logger.error(f"Server error: {e}", exc_info=self.debug)
            return 1
        finally:
            await self.shutdown()

        return 0


def main():
    """Main entry point for the MCP server."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the MCP Server")
    parser.add_argument(
        "--host", type=str, default=os.getenv("HOST", "0.0.0.0"), help="Host to bind the server to"
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=int(os.getenv("PORT", 8000)),
        help="Port to bind the server to",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=os.getenv("DEBUG", "").lower() in ("true", "1", "t"),
        help="Enable debug mode",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=os.getenv("LOG_LEVEL", "INFO"),
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level",
    )

    args = parser.parse_args()

    # Configure logging
    logging.getLogger().setLevel(args.log_level)

    # Create and run the server
    server = MCPServer(host=args.host, port=args.port, debug=args.debug)

    try:
        return asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return 0
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=args.debug)
        return 1


if __name__ == "__main__":
    sys.exit(main())
