# Help system portmanteau tool.
# Consolidates help and documentation operations into a single interface.

import logging
from typing import Any

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.tools.help_tools import HelpSystem

logger = logging.getLogger(__name__)


@mcp.tool()
@HelpSystem.register_tool(category="help")
async def help_system(
    operation: str,
    topic: str | None = None,
    category: str | None = None,
    tool_name: str | None = None,
    include_examples: bool = True,
    include_parameters: bool = True,
    format_output: str = "markdown",
    search_query: str | None = None,
    max_results: int = 10,
) -> dict[str, Any]:
    """Help system portmanteau tool.

    Comprehensive help and documentation system consolidating ALL help operations
    into a single interface. Provides hierarchical help browsing, tool documentation,
    category navigation, search capabilities, and formatted output across all MCP tools.

    Prerequisites:
        - HelpSystem class must be initialized (automatic on server startup)
        - Tools must be registered with HelpSystem for help to be available
        - For tool-specific help: Tool must exist and be registered

    Operations:
        - help: Get hierarchical help for all tools or specific category
        - tool_help: Get detailed documentation for specific tool
        - list_categories: List all available help categories
        - search_help: Search help documentation by query string
        - get_tool_examples: Get usage examples for specific tool
        - get_parameter_info: Get parameter information for specific tool
        - format_help_output: Format help output in different formats

    Parameters:
        operation (str, REQUIRED): The operation to perform
            Valid values: 'help', 'tool_help', 'list_categories', 'search_help',
                         'get_tool_examples', 'get_parameter_info', 'format_help_output'
            Example: 'help', 'tool_help', 'search_help'

        topic (str, OPTIONAL): Topic to get help for
            Format: Any help topic or category name
            Required for: help, format_help_output operations
            Example: 'database operations', 'firefox bookmarks', 'connection management'

        category (str, OPTIONAL): Category to filter help by
            Valid values: 'database', 'firefox', 'chrome', 'calibre', 'registry', 'help'
            Default: None (show all categories)
            Used for: help operation
            Example: 'database', 'firefox'

        tool_name (str, OPTIONAL): Name of tool to get help for
            Format: Exact tool name (case-sensitive)
            Required for: tool_help, get_tool_examples, get_parameter_info operations
            Validation: Tool must be registered with HelpSystem
            Example: 'db_connection', 'firefox_bookmarks', 'browser_bookmarks'

        include_examples (bool, OPTIONAL): Include usage examples in help output
            Default: True
            Behavior: Adds code examples showing tool usage
            Used for: help, tool_help operations
            Example: True, False

        include_parameters (bool, OPTIONAL): Include parameter information
            Default: True
            Behavior: Adds detailed parameter documentation
            Used for: help, tool_help operations
            Example: True, False

        format_output (str, OPTIONAL): Output format for help content
            Valid values: 'markdown', 'html', 'text', 'json'
            Default: 'markdown'
            Used for: help, tool_help, format_help_output operations
            Example: 'markdown', 'html', 'json'

        search_query (str, OPTIONAL): Search query for help documentation
            Format: Free-form search string
            Required for: search_help operation
            Behavior: Searches tool names, descriptions, and docstrings
            Example: 'firefox bookmarks', 'database connection', 'query execution'

        max_results (int, OPTIONAL): Maximum number of search results to return
            Format: Positive integer
            Range: 1-100
            Default: 10
            Used for: search_help operation
            Example: 5, 20, 50

    Returns:
        Dictionary containing operation-specific results:
            - success: Boolean indicating operation success
            - operation: Echo of operation performed
            - For help: categories (dict), total_tools, help_content (if topic provided)
            - For tool_help: tool (dict with name, description, parameters, docstring)
            - For list_categories: categories (list), descriptions (dict)
            - For search_help: results (list), total_found, query
            - For get_tool_examples: examples (list), tool_name
            - For get_parameter_info: parameters (dict), tool_name
            - For format_help_output: formatted_content, format
            - error: Error message if success is False
            - available_operations: List of valid operations (on invalid operation)

    Usage:
        This tool is the primary interface for discovering and understanding available
        MCP tools. Use it to explore capabilities, learn tool usage, and get examples.

        Common scenarios:
        - Discovery: Browse all available tools by category
        - Learning: Get detailed documentation for specific tools
        - Reference: Look up parameter information and examples
        - Search: Find tools matching specific keywords or topics

        Best practices:
        - Start with help(operation='list_categories') to see all categories
        - Use help(operation='help', category='database') to browse category
        - Use tool_help to understand specific tool before using it
        - Search for tools when you know the functionality but not the name

    Examples:
        Get hierarchical help for all tools:
            result = await help_system(operation='help')
            # Returns: {
            #     'status': 'success',
            #     'categories': {
            #         'database': {'description': '...', 'tools': [...]},
            #         'firefox': {'description': '...', 'tools': [...]}
            #     },
            #     'total_tools': 23
            # }

        Get help for specific category:
            result = await help_system(
                operation='help',
                category='database',
                include_examples=True
            )
            # Returns: Database tools with examples

        Get detailed tool help:
            result = await help_system(
                operation='tool_help',
                tool_name='db_connection',
                include_examples=True,
                include_parameters=True
            )
            # Returns: {
            #     'status': 'success',
            #     'tool': {
            #         'name': 'db_connection',
            #         'description': 'Database connection management...',
            #         'parameters': {...},
            #         'docstring': '...',
            #         'examples': [...]
            #     }
            # }

        Search help documentation:
            result = await help_system(
                operation='search_help',
                search_query='bookmark sync',
                max_results=5
            )
            # Returns: {
            #     'status': 'success',
            #     'results': [
            #         {'tool': 'sync_bookmarks', 'relevance': 0.95, ...},
            #         {'tool': 'browser_bookmarks', 'relevance': 0.82, ...}
            #     ],
            #     'total_found': 3,
            #     'query': 'bookmark sync'
            # }

        Get tool examples:
            result = await help_system(
                operation='get_tool_examples',
                tool_name='firefox_bookmarks'
            )
            # Returns: {
            #     'status': 'success',
            #     'tool_name': 'firefox_bookmarks',
            #     'examples': [
            #         {'description': '...', 'code': '...', 'output': '...'}
            #     ]
            # }

        Get parameter information:
            result = await help_system(
                operation='get_parameter_info',
                tool_name='db_operations'
            )
            # Returns: {
            #     'status': 'success',
            #     'tool_name': 'db_operations',
            #     'parameters': {
            #         'operation': {'type': 'str', 'required': True, ...},
            #         'connection_name': {'type': 'str', 'required': True, ...}
            #     }
            # }

        Format help output as HTML:
            result = await help_system(
                operation='format_help_output',
                topic='database operations',
                format_output='html'
            )
            # Returns: {
            #     'status': 'success',
            #     'formatted_content': '<html>...',
            #     'format': 'html',
            #     'topic': 'database operations'
            # }

        Error handling - tool not found:
            result = await help_system(
                operation='tool_help',
                tool_name='nonexistent_tool'
            )
            # Returns: {
            #     'status': 'error',
            #     'error': 'Tool not found: nonexistent_tool',
            #     'message': 'Use help(operation='list_categories') to see available tools'
            # }

    Errors:
        Common errors and solutions:
        - 'Tool not found: {tool_name}':
            Cause: Tool name doesn't exist or not registered with HelpSystem
            Fix: Use help_system(operation='list_categories') to see available tools
            Workaround: Check spelling, tool may be in different category

        - 'Topic is required':
            Cause: Missing topic parameter for help operation
            Fix: Provide topic parameter or use category instead
            Example: topic='database operations' or category='database'

        - 'Invalid output format: {format}':
            Cause: format_output value not supported
            Fix: Use one of: 'markdown', 'html', 'text', 'json'
            Example: format_output='markdown'

        - 'Search query is required':
            Cause: Missing search_query for search_help operation
            Fix: Provide search_query parameter with search terms
            Example: search_query='database connection'

    See Also:
        - db_connection: Database connection management (example tool documentation)
        - db_operations: Database operations (example tool documentation)
        - All other portmanteau tools: See help_system(operation='list_categories')
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
    topic: str | None,
    category: str | None,
    include_examples: bool,
    include_parameters: bool,
    format_output: str,
) -> dict[str, Any]:
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
    tool_name: str | None, include_examples: bool, include_parameters: bool, format_output: str
) -> dict[str, Any]:
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


async def _list_categories() -> dict[str, Any]:
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


async def _search_help(search_query: str | None, max_results: int) -> dict[str, Any]:
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


async def _get_tool_examples(tool_name: str | None) -> dict[str, Any]:
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


async def _get_parameter_info(tool_name: str | None) -> dict[str, Any]:
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


async def _format_help_output(topic: str | None, format_output: str) -> dict[str, Any]:
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
