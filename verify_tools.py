import asyncio
import logging
from database_operations_mcp.main import DatabaseOperationsMCP

# Configure logging to see import errors
logging.basicConfig(level=logging.INFO)


async def verify_tools():
    print("\n🔍 VERIFYING SOTA TOOL REGISTRATION...")
    server = DatabaseOperationsMCP()
    # Access the FastMCP instance
    mcp_instance = server.mcp

    # Get all registered tools
    # In FastMCP 3.0, tools are in mcp_instance._tools or similar
    # We can use the inspect utility if available, or just check the internal registry
    try:
        from fastmcp.utilities.inspect import get_tools

        tools = get_tools(mcp_instance)
    except ImportError:
        # Fallback to internal registry
        tools = mcp_instance._tool_manager.list_tools()

    print(f"✅ Total tools registered: {len(tools)}")
    print("\nREGISTERED TOOLS:")
    for i, tool in enumerate(tools, 1):
        print(f"{i:2d}. {tool.name}")

    if len(tools) >= 19:
        print("\n✨ SUCCESS: All 19+ portmanteau tools are registered!")
    else:
        print(f"\n⚠️ WARNING: Only {len(tools)} tools registered. Missing {19 - len(tools)}+ tools.")


if __name__ == "__main__":
    asyncio.run(verify_tools())
