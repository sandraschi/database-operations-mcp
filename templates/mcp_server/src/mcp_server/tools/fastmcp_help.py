"""
FastMCP Help Tool

This module provides a FastMCP 2.13 compliant help tool that can be called via stdio.
It provides information about available tools and their usage.
"""

import asyncio
import inspect
import json
import logging
from typing import Any, Callable, Dict, Optional

# Import FastMCP types
try:
    from mcp.server.fastmcp import FastMCP
    from mcp.server.fastmcp.server import get_logger
    from mcp.types import Tool as MCPTool
    from mcp.types import ToolCall, ToolDefinition, ToolError, ToolResult
except ImportError:
    # Fallback for development
    from typing import Any, TypedDict

    class ToolCall(TypedDict):
        id: str
        name: str
        arguments: Dict[str, Any]

    class ToolResult(TypedDict):
        id: str
        result: Any

    class ToolError(TypedDict):
        id: str
        error: str

    class ToolDefinition(TypedDict):
        name: str
        description: str
        parameters: Dict[str, Any]

    class MCPTool:
        def __init__(self, name: str, description: str, parameters: Dict[str, Any], func: Callable):
            self.name = name
            self.description = description
            self.parameters = parameters
            self.func = func

        async def __call__(self, **kwargs) -> Any:
            return await self.func(**kwargs)


logger = get_logger(__name__) if "get_logger" in globals() else logging.getLogger(__name__)


class FastMCPHelpTool(MCPTool):
    """FastMCP 2.13 compliant help tool."""

    def __init__(self, server: "FastMCP"):
        """Initialize the help tool.

        Args:
            server: The FastMCP server instance.
        """
        self.server = server

        # Define the tool schema
        tool_definition = ToolDefinition(
            name="help",
            description="Get help about available tools and their usage.",
            parameters={
                "type": "object",
                "properties": {
                    "tool_name": {
                        "type": "string",
                        "description": (
                            "Name of the tool to get help for. "
                            "If not provided, lists all available tools."
                        ),
                    },
                    "search_term": {
                        "type": "string",
                        "description": "Search term to filter tools by name or description.",
                    },
                    "detailed": {
                        "type": "boolean",
                        "description": "Whether to include detailed information about each tool.",
                        "default": False,
                    },
                },
                "additionalProperties": False,
            },
        )

        super().__init__(
            name=tool_definition["name"],
            description=tool_definition["description"],
            parameters=tool_definition["parameters"],
            func=self._execute,
        )

    async def _execute(
        self,
        tool_name: Optional[str] = None,
        search_term: Optional[str] = None,
        detailed: bool = False,
    ) -> Dict[str, Any]:
        """Execute the help tool.

        Args:
            tool_name: Name of the tool to get help for.
            search_term: Search term to filter tools by name or description.
            detailed: Whether to include detailed information about each tool.

        Returns:
            A dictionary containing the help information.
        """
        if tool_name:
            return await self._get_tool_help(tool_name)
        else:
            return await self._list_tools(search_term, detailed)

    async def _get_tool_help(self, tool_name: str) -> Dict[str, Any]:
        """Get detailed help for a specific tool.

        Args:
            tool_name: Name of the tool to get help for.

        Returns:
            A dictionary containing the tool's help information.
        """
        # Get the tool from the server
        tool = self.server.get_tool(tool_name)
        if not tool:
            return {"error": f"No tool named '{tool_name}' found."}

        # Get the tool's definition
        tool_def = (
            tool.definition
            if hasattr(tool, "definition")
            else {
                "name": getattr(tool, "name", tool_name),
                "description": getattr(tool, "description", "No description available."),
                "parameters": getattr(tool, "parameters", {}),
            }
        )

        # Format the help information
        help_info = {
            "name": tool_def["name"],
            "description": tool_def.get("description", "No description available."),
            "parameters": tool_def.get("parameters", {}),
        }

        # Add additional metadata if available
        if hasattr(tool, "__doc__") and tool.__doc__:
            help_info["docstring"] = inspect.cleandoc(tool.__doc__)

        if hasattr(tool, "examples") and tool.examples:
            help_info["examples"] = tool.examples

        return help_info

    async def _list_tools(
        self,
        search_term: Optional[str] = None,
        detailed: bool = False,
    ) -> Dict[str, Any]:
        """List all available tools.

        Args:
            search_term: Search term to filter tools by name or description.
            detailed: Whether to include detailed information about each tool.

        Returns:
            A dictionary containing the list of tools and their information.
        """
        tools = self.server.get_tools()

        # Filter tools by search term if provided
        if search_term:
            search_term = search_term.lower()
            tools = {
                name: tool
                for name, tool in tools.items()
                if (
                    search_term in name.lower()
                    or search_term in getattr(tool, "description", "").lower()
                    or search_term in getattr(tool, "__doc__", "").lower()
                )
            }

        # Sort tools by name
        sorted_tools = sorted(tools.items(), key=lambda x: x[0])

        # Format the tool information
        result = {
            "tools": [
                await self._get_tool_help(name)
                if detailed
                else {
                    "name": name,
                    "description": getattr(tool, "description", "No description available."),
                }
                for name, tool in sorted_tools
            ]
        }

        return result


def register_tool(server: "FastMCP") -> MCPTool:
    """Register the help tool with the FastMCP server.

    This function is called by the FastMCP server to register the tool.

    Args:
        server: The FastMCP server instance.

    Returns:
        The registered tool instance.
    """
    tool = FastMCPHelpTool(server)
    server.register_tool(tool)
    return tool


# For testing the tool directly
if __name__ == "__main__":
    import asyncio

    # Create a mock server for testing
    class MockServer:
        def __init__(self):
            self.tools = {}

        def get_tool(self, name: str):
            return self.tools.get(name)

        def get_tools(self) -> Dict[str, Any]:
            return self.tools

        def register_tool(self, tool):
            self.tools[tool.name] = tool

    async def test_help_tool():
        # Create a mock server with some tools
        server = MockServer()

        # Register the help tool
        help_tool = FastMCPHelpTool(server)
        server.register_tool(help_tool)

        # Test listing all tools
        print("Testing list_tools():")
        result = await help_tool._list_tools()
        print(json.dumps(result, indent=2))

        # Test getting help for a specific tool
        print("\nTesting get_tool_help('help'):")
        result = await help_tool._get_tool_help("help")
        print(json.dumps(result, indent=2))

    # Run the test
    asyncio.run(test_help_tool())
