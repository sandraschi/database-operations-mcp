"""
Help system for Database Operations MCP.
Provides interactive help and documentation for all available tools.
"""

import inspect
import re
from typing import Any, Callable, Dict, Optional, TypeVar, Union

# Import the global MCP instance
from database_operations_mcp.config.mcp_config import mcp

# Type variable for function type
F = TypeVar("F", bound=Callable[..., Any])


class HelpSystem:
    """Centralized help system for MCP tools."""

    _tools = {}
    _categories = {
        "database": "Core database operations",
        "firefox": "Firefox bookmark tools",
        "calibre": "Calibre library tools",
        "registry": "Windows Registry tools",
        "help": "Help and documentation",
    }

    @classmethod
    def register_tool(
        cls, tool_func: Optional[F] = None, *, category: str = "database"
    ) -> Union[Callable[[F], F], F]:
        """Register a tool with its documentation.

        Args:
            tool_func: The tool function to register
            category: Category for the tool (default: 'database')

        Returns:
            The decorated function or a decorator
        """

        def decorator(func: F) -> F:
            doc = inspect.getdoc(func) or ""
            name = func.__name__

            # Parse the docstring
            description = doc.split("\n")[0] if doc else "No description"

            # Parse parameters from docstring
            params = {}
            param_section = re.search(r"Args:(.*?)(?=\n\w+:|\Z)", doc, re.DOTALL)
            if param_section:
                param_lines = [
                    line.strip() for line in param_section.group(1).split("\n") if line.strip()
                ]
                for line in param_lines:
                    if ":" in line:
                        param_name, param_desc = line.split(":", 1)
                        param_name = param_name.strip()
                        param_desc = param_desc.strip()
                        params[param_name] = param_desc

            # Store tool metadata
            cls._tools[name] = {
                "name": name,
                "description": description,
                "docstring": doc,
                "parameters": params,
                "category": category.lower(),
            }
            return func

        return decorator(tool_func) if tool_func else decorator

    @classmethod
    def get_help(cls, category: Optional[str] = None) -> Dict[str, Any]:
        """Get help for all tools or filter by category.

        Args:
            category: Optional category to filter tools

        Returns:
            Dictionary with help information
        """
        if category:
            category = category.lower()
            tools = {
                name: info for name, info in cls._tools.items() if info["category"] == category
            }
        else:
            tools = cls._tools

        # Group tools by category
        categorized = {}
        for tool_name, tool_info in tools.items():
            cat = tool_info["category"]
            if cat not in categorized:
                categorized[cat] = {
                    "description": cls._categories.get(cat, "Uncategorized"),
                    "tools": [],
                }
            categorized[cat]["tools"].append(
                {"name": tool_name, "description": tool_info["description"]}
            )

        return {"status": "success", "categories": categorized, "total_tools": len(tools)}

    @classmethod
    def get_tool_help(cls, tool_name: str) -> Dict[str, Any]:
        """Get detailed help for a specific tool.

        Args:
            tool_name: Name of the tool to get help for

        Returns:
            Dictionary with detailed tool information
        """
        if tool_name not in cls._tools:
            return {"status": "error", "error": f"Tool not found: {tool_name}"}

        tool_info = cls._tools[tool_name]
        return {
            "status": "success",
            "tool": {
                "name": tool_info["name"],
                "description": tool_info["description"],
                "category": tool_info["category"],
                "category_description": cls._categories.get(tool_info["category"], ""),
                "parameters": tool_info["parameters"],
                "docstring": tool_info["docstring"],
            },
        }


# Register tools using the @mcp.tool decorator
# The mcp instance is imported from the centralized config


@mcp.tool()
@HelpSystem.register_tool(category="help")
async def help(category: Optional[str] = None) -> Dict[str, Any]:
    """Get hierarchical help for all tools or specific category.

    Provides comprehensive help documentation for all available MCP tools,
    organized by category. Essential starting point for discovering capabilities.

    Parameters:
        category: Category filter (default: None)
            - None: Show all tools
            - 'database': Core database operations
            - 'firefox': Firefox bookmark tools (profiles, bookmarks, 
              curated collections, portmanteau profiles)
            - 'calibre': Calibre library tools
            - 'registry': Windows Registry tools
            - 'help': Help and documentation tools

    Returns:
        Dictionary containing:
            - status: 'success' (always succeeds)
            - categories: Dictionary of categories with:
                - description: Category description
                - tools: List of tools in category with name and description
            - total_tools: Count of tools returned

    Usage:
        Use this as your first stop to discover available tools and their purposes.
        Filter by category to narrow down to specific functionality areas.

        Common scenarios:
        - Discover available database tools
        - Find tools for specific tasks
        - Learn tool capabilities
        - Browse tools by category
        - Discover Firefox profile and bookmark management features

    Examples:
        Get all available tools:
            result = await help()
            # Returns: {
            #     'status': 'success',
            #     'categories': {
            #         'database': {
            #             'description': 'Core database operations',
            #             'tools': [
            #                 {'name': 'execute_query', 
            #                  'description': 'Execute SQL or NoSQL query...'},
            #                 {'name': 'list_tables', 
            #                  'description': 'List all tables/collections...'}
            #             ]
            #         },
            #         'firefox': {...}
            #     },
            #     'total_tools': 64
            # }

        Filter by category:
            result = await help(category="database")
            # Returns: Only database-related tools

        Find specific functionality:
            result = await help(category="firefox")
            for tool in result['categories']['firefox']['tools']:
                if 'bookmark' in tool['description']:
                    print(f"Found: {tool['name']}")

    Notes:
        - Categories are predefined (database, firefox, calibre, registry, help)
        - Tool descriptions are first line of docstrings
        - Use tool_help for detailed information about specific tools

    See Also:
        - tool_help: Get detailed help for specific tool
    """
    return HelpSystem.get_help(category)


@mcp.tool()
@HelpSystem.register_tool(category="help")
async def tool_help(tool_name: str) -> Dict[str, Any]:
    """Get detailed documentation for specific tool.

    Retrieves complete documentation for a single tool including description,
    parameters, return values, and full docstring with examples.

    Parameters:
        tool_name: Name of tool to get help for
            - Must be exact tool name
            - Case-sensitive
            - Use help() to discover tool names

    Returns:
        Dictionary containing:
            - status: 'success' or 'error'
            - tool: Tool information dictionary with:
                - name: Tool name
                - description: Brief description
                - category: Tool category
                - category_description: Category explanation
                - parameters: Dictionary of parameters
                - docstring: Complete docstring text
            - error: Error message if tool not found

    Usage:
        Use this to get detailed information about a specific tool before using it.
        Shows complete docstring including usage examples and notes.

        Common scenarios:
        - Learn how to use specific tool
        - Understand tool parameters
        - See usage examples
        - Check tool category

    Examples:
        Get help for execute_query:
            result = await tool_help("execute_query")
            # Returns: {
            #     'status': 'success',
            #     'tool': {
            #         'name': 'execute_query',
            #         'description': 'Execute SQL or NoSQL query...',
            #         'category': 'database',
            #         'parameters': {
            #             'connection_name': 'Name of registered database connection...',
            #             'query': 'SQL or database-specific query...'
            #         },
            #         'docstring': '... full docstring with examples ...'
            #     }
            # }

        Check if tool exists:
            result = await tool_help("my_tool")
            if result['status'] == 'error':
                print("Tool not found, use help() to see available tools")

        Read tool docstring:
            result = await tool_help("list_tables")
            if result['status'] == 'success':
                print(result['tool']['docstring'])
                # Displays: Complete docstring with all sections

    Notes:
        - Returns full docstring text including examples
        - Tool names are case-sensitive
        - Use help() first to discover tool names

    See Also:
        - help: Browse all tools by category
    """
    return HelpSystem.get_tool_help(tool_name)
