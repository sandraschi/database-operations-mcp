"""
FastMCP 2.13 Server

This module provides the command-line interface for the FastMCP 2.13 server.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mcp_server.fastmcp_server import create_fastmcp_server


def main() -> int:
    """Main entry point for the FastMCP server."""
    import argparse

    # Set up argument parsing
    parser = argparse.ArgumentParser(description="FastMCP 2.13 Server")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    # Parse command line arguments
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create and start the server
    server = create_fastmcp_server(debug=args.debug)

    try:
        return asyncio.run(server.start())
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
        return 0
    except Exception as e:
        logging.error(f"Server error: {e}", exc_info=args.debug)
        return 1


if __name__ == "__main__":
    sys.exit(main())
