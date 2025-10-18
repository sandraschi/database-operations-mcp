import logging
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


def test_imports():
    """Test importing all modules and registering tools."""
    try:
        logger.info("Testing imports...")

        # Add the parent directory to the path
        parent_dir = str(Path(__file__).parent.resolve() / "src")
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        # Import FastMCP
        from fastmcp import FastMCP

        logger.info("Successfully imported FastMCP")

        # Create FastMCP instance
        mcp = FastMCP("test-mcp", "Test MCP Server", version="0.1.0")
        logger.info("Created FastMCP instance")

        # Import the register_all_tools function
        from database_operations_mcp.handlers import register_all_tools

        logger.info("Imported register_all_tools")

        # Register tools
        logger.info("Registering tools...")
        register_all_tools(mcp)

        # List registered tools
        from fastmcp.utilities.inspect import get_tools

        tools = get_tools(mcp)
        logger.info(f"Successfully registered {len(tools)} tools")

        for tool_name, _tool_info in tools.items():
            logger.info(f"Tool: {tool_name}")

        return True

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
