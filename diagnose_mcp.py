import asyncio
import sys
import os

# Add src to sys.path
sys.path.append(os.path.join(os.getcwd(), "src"))

from database_operations_mcp.main import DatabaseOperationsMCP


async def diagnose():
    try:
        print("Initializing DatabaseOperationsMCP...")
        # Mock some environment variables if needed
        os.environ["DATABASE_TYPE"] = "sqlite"

        app = DatabaseOperationsMCP()
        mcp = app.mcp

        print(f"FastMCP instance name: {mcp.name}")

        # Try to list tools directly from the app
        tools = []

        # FastMCP 3.0 methods
        try:
            from fastmcp.utilities.inspect import get_tools

            tools = get_tools(mcp)
            print("Found tools via fastmcp.utilities.inspect.get_tools(mcp)")
        except ImportError:
            print("Could not import fastmcp.utilities.inspect.get_tools")

        if not tools:
            if hasattr(mcp, "get_tools") and callable(mcp.get_tools):
                tools = mcp.get_tools()
                print("Found tools via mcp.get_tools()")
            elif hasattr(mcp, "list_tools") and callable(mcp.list_tools):
                tools = mcp.list_tools()
                print("Found tools via mcp.list_tools()")
            elif hasattr(mcp, "_tool_manager"):
                if hasattr(mcp._tool_manager, "get_tools"):
                    tools = mcp._tool_manager.get_tools()
                    print("Found tools via mcp._tool_manager.get_tools()")
                elif hasattr(mcp._tool_manager, "list_tools"):
                    tools = mcp._tool_manager.list_tools()
                    print("Found tools via mcp._tool_manager.list_tools()")

        print(f"\nRegistered tools ({len(tools)}):")
        for i, t in enumerate(tools, 1):
            name = getattr(t, "name", str(t))
            print(f"{i:2d}. {name}")

    except Exception as e:
        print(f"ERROR during diagnosis: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(diagnose())
