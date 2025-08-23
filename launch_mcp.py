#!/usr/bin/env python3
"""Launcher script for Database Operations MCP server."""
import sys
import logging
import asyncio
from database_operations_mcp.main import DatabaseOperationsMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

async def main():
    """Main entry point for the MCP server."""
    server = DatabaseOperationsMCP()
    await server.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("MCP server stopped by user")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
