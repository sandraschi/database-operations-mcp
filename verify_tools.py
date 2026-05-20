import asyncio
import logging
import sys
import io

# Set stdout to UTF-8 to avoid encoding issues with emojis
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from database_operations_mcp.main import DatabaseOperationsMCP

# Configure logging to see import errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_tools():
    print("\n🔍 VERIFYING SOTA TOOL REGISTRATION...")
    try:
        server = DatabaseOperationsMCP()
        # Access the FastMCP instance
        mcp_instance = server.mcp

        # Get all registered tools using FastMCP 3.x API
        tools = await mcp_instance.list_tools()
        
        print(f"✅ Total tools registered: {len(tools)}")
        print("\nREGISTERED TOOLS:")
        for i, tool in enumerate(tools, 1):
            print(f"{i:2d}. {tool.name}")

        if len(tools) >= 19:
            print("\n✨ SUCCESS: All 19+ portmanteau tools are registered!")
        else:
            print(f"\n⚠️ WARNING: Only {len(tools)} tools registered. Missing {19 - len(tools)}+ tools.")
            
    except Exception as e:
        logger.error(f"Failed to verify tools: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(verify_tools())
