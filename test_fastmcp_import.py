#!/usr/bin/env python3
"""Test script for FastMCP import and basic functionality."""

import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


def test_fastmcp_import():
    """Test FastMCP import and version."""
    try:
        import fastmcp

        logger.info("FastMCP imported successfully")
        logger.info(f"FastMCP version: {fastmcp.__version__}")

        # Test creating a FastMCP instance
        logger.info("Testing FastMCP initialization...")
        mcp = fastmcp.FastMCP(name="test-mcp", description="Test MCP instance", version="0.1.0")
        logger.info("FastMCP instance created successfully")
        return True

    except ImportError as e:
        logger.error(f"Failed to import FastMCP: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    logger.info("Testing FastMCP import and initialization...")
    success = test_fastmcp_import()
    sys.exit(0 if success else 1)
