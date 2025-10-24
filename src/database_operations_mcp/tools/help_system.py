# Help system portmanteau tool.
# Consolidates help and documentation operations into a single interface.

import logging
from typing import Any, Dict, List, Optional

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.tools.help_tools import HelpSystem

logger = logging.getLogger(__name__)


@mcp.tool()
@HelpSystem.register_tool(category="help")
async def help_system(
    operation: str,
    topic: Optional[str] = None,
    category: Optional[str] = None,
    tool_name: Optional[str] = None,
    include_examples: bool = True,
    include_parameters: bool = True,
    format_output: str = "markdown",
    search_query: Optional[str] = None,
    max_results: int = 10,
) -> Dict[str, Any]:
    """Help system portmanteau tool.

    This tool consolidates all help and documentation operations into a single interface,
    providing unified access to help system functionality.

    Operations:
    - help: Get help for a specific topic or tool
    - tool_help: Get detailed help for a specific tool
    - list_categories: List all available help categories
    - search_help: Search help documentation
    - get_tool_examples: Get usage examples for tools
    - get_parameter_info: Get parameter information for tools
    - format_help_output: Format help output in different formats

    Args:
        operation: The operation to perform (required)
        topic: Topic to get help for
        category: Category to filter by
        tool_name: Name of the tool to get help for
        include_examples: Whether to include usage examples
        include_parameters: Whether to include parameter information
        format_output: Output format (markdown, html, text, json)
        search_query: Search query for help documentation
        max_results: Maximum number of results to return

    Returns:
        Dictionary with operation results and help information

    Examples:
        Get general help:
        help_system(operation='help', topic='database operations')

        Get tool help:
        help_system(operation='tool_help', tool_name='db_connection',
                   include_examples=True, include_parameters=True)

        List categories:
        help_system(operation='list_categories')

        Search help:
        help_system(operation='search_help', search_query='firefox bookmarks',
                   max_results=5)

        Get tool examples:
        help_system(operation='get_tool_examples', tool_name='firefox_bookmarks')

        Get parameter info:
        help_system(operation='get_parameter_info', tool_name='db_operations')

        Format help output:
        help_system(operation='format_help_output', topic='database',
                   format_output='html')
    """

    if operation == "help":
        return await _get_help(topic, category, include_examples, include_parameters, format_output)
    elif operation == "tool_help":
        return await _get_tool_help(tool_name, include_examples, include_parameters, format_output)
    elif operation == "list_categories":
        return await _list_categories()
    elif operation == "search_help":
        return await _search_help(search_query, max_results)
    elif operation == "get_tool_examples":
        return await _get_tool_examples(tool_name)
    elif operation == "get_parameter_info":
        return await _get_parameter_info(tool_name)
    elif operation == "format_help_output":
        return await _format_help_output(topic, format_output)
    else:
        return {
            "success": False,
            "error": f"Unknown operation: {operation}",
            "available_operations": [
                "help",
                "tool_help",
                "list_categories",
                "search_help",
                "get_tool_examples",
                "get_parameter_info",
                "format_help_output",
            ],
        }


async def _get_help(
    topic: Optional[str],
    category: Optional[str],
    include_examples: bool,
    include_parameters: bool,
    format_output: str,
) -> Dict[str, Any]:
    """Get help for a specific topic or tool."""
    try:
        if not topic:
            raise ValueError("Topic is required")

        return {
            "success": True,
            "message": f"Help requested for topic '{topic}'",
            "topic": topic,
            "category": category,
            "include_examples": include_examples,
            "include_parameters": include_parameters,
            "format_output": format_output,
            "help_content": f"# Help for {topic}\n\nThis is placeholder help content for {topic}.",
            "note": "Implementation pending - requires help content generation",
        }

    except Exception as e:
        logger.error(f"Error getting help: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to get help: {str(e)}",
            "topic": topic,
            "help_content": "",
        }


async def _get_tool_help(
    tool_name: Optional[str], include_examples: bool, include_parameters: bool, format_output: str
) -> Dict[str, Any]:
    """Get detailed help for a specific tool."""
    try:
        if not tool_name:
            raise ValueError("Tool name is required")

        return {
            "success": True,
            "message": f"Tool help requested for '{tool_name}'",
            "tool_name": tool_name,
            "include_examples": include_examples,
            "include_parameters": include_parameters,
            "format_output": format_output,
            "tool_help": {
                "description": f"Detailed help for {tool_name}",
                "parameters": [] if not include_parameters else ["operation", "param1", "param2"],
                "examples": [] if not include_examples else [f"{tool_name}(operation='example')"],
                "note": "Implementation pending - requires tool help extraction",
            },
        }

    except Exception as e:
        logger.error(f"Error getting tool help: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to get tool help: {str(e)}",
            "tool_name": tool_name,
            "tool_help": {},
        }


async def _list_categories() -> Dict[str, Any]:
    """List all available help categories."""
    try:
        return {
            "success": True,
            "message": "Help categories listed",
            "categories": [
                {"name": "database", "description": "Database operations and management"},
                {"name": "firefox", "description": "Firefox bookmark and profile management"},
                {"name": "media", "description": "Media library operations (Calibre, Plex)"},
                {"name": "windows", "description": "Windows system and registry operations"},
                {"name": "help", "description": "Help system and documentation"},
            ],
            "count": 5,
        }

    except Exception as e:
        logger.error(f"Error listing categories: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to list categories: {str(e)}",
            "categories": [],
            "count": 0,
        }


async def _search_help(search_query: Optional[str], max_results: int) -> Dict[str, Any]:
    """Search help documentation."""
    try:
        if not search_query:
            raise ValueError("Search query is required")

        return {
            "success": True,
            "message": f"Help search completed for '{search_query}'",
            "search_query": search_query,
            "max_results": max_results,
            "results": [
                {
                    "title": f"Help result for {search_query}",
                    "content": f"This is a search result for {search_query}",
                    "category": "general",
                    "relevance": 0.9,
                }
            ],
            "count": 1,
            "note": "Implementation pending - requires help search indexing",
        }

    except Exception as e:
        logger.error(f"Error searching help: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to search help: {str(e)}",
            "search_query": search_query,
            "results": [],
            "count": 0,
        }


async def _get_tool_examples(tool_name: Optional[str]) -> Dict[str, Any]:
    """Get usage examples for tools."""
    try:
        if not tool_name:
            raise ValueError("Tool name is required")

        return {
            "success": True,
            "message": f"Tool examples requested for '{tool_name}'",
            "tool_name": tool_name,
            "examples": [
                {
                    "description": f"Basic usage of {tool_name}",
                    "code": f"{tool_name}(operation='example')",
                    "explanation": f"This shows basic usage of the {tool_name} tool",
                }
            ],
            "count": 1,
            "note": "Implementation pending - requires example extraction",
        }

    except Exception as e:
        logger.error(f"Error getting tool examples: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to get tool examples: {str(e)}",
            "tool_name": tool_name,
            "examples": [],
            "count": 0,
        }


async def _get_parameter_info(tool_name: Optional[str]) -> Dict[str, Any]:
    """Get parameter information for tools."""
    try:
        if not tool_name:
            raise ValueError("Tool name is required")

        return {
            "success": True,
            "message": f"Parameter info requested for '{tool_name}'",
            "tool_name": tool_name,
            "parameters": [
                {
                    "name": "operation",
                    "type": "str",
                    "required": True,
                    "description": "The operation to perform",
                },
                {
                    "name": "param1",
                    "type": "Optional[str]",
                    "required": False,
                    "description": "Optional parameter 1",
                },
            ],
            "count": 2,
            "note": "Implementation pending - requires parameter introspection",
        }

    except Exception as e:
        logger.error(f"Error getting parameter info: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to get parameter info: {str(e)}",
            "tool_name": tool_name,
            "parameters": [],
            "count": 0,
        }


async def _format_help_output(topic: Optional[str], format_output: str) -> Dict[str, Any]:
    """Format help output in different formats."""
    try:
        if not topic:
            raise ValueError("Topic is required")

        return {
            "success": True,
            "message": f"Help output formatted for '{topic}'",
            "topic": topic,
            "format_output": format_output,
            "formatted_content": f"Formatted help content for {topic} in {format_output} format",
            "note": "Implementation pending - requires output formatting logic",
        }

    except Exception as e:
        logger.error(f"Error formatting help output: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to format help output: {str(e)}",
            "topic": topic,
            "format_output": format_output,
            "formatted_content": "",
        }
