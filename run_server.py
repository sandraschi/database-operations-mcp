#!/usr/bin/env python3
"""Standalone launcher for Database Operations MCP."""

import logging
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def main():
    try:
        # Add src to path
        project_root = os.path.dirname(os.path.abspath(__file__))
        src_path = os.path.join(project_root, "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        logger.info(f"Python path: {sys.path}")

        # Try to import and run the main module
        logger.info("Attempting to import database_operations_mcp...")
        from database_operations_mcp.main import main as mcp_main

        logger.info("Starting MCP server...")
        mcp_main()

    except ImportError as e:
        logger.error(f"Import error: {e}", exc_info=True)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Runtime error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
