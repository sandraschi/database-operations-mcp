"""
Help system for Database Operations MCP.

Provides interactive help and documentation for all available tools.
"""

from typing import Dict, List, Optional, Any
from fastmcp import mcp_tool
import inspect
import json
from pathlib import Path

# This will be populated with tool metadata
TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {}

class HelpSystem:
    """Centralized help system for database operations MCP tools."""
    
    _tools = {}
    _categories = {
        'database': 'Core database operations',
        'connection': 'Database connection management',
        'data': 'Data manipulation and querying',
        'fts': 'Full-text search operations',
        'help': 'Help and documentation',
        'admin': 'Administrative functions'
    }
    
    @classmethod
    def register_tool(cls, tool_func, category: str = 'database'):
        """Register a tool with its help documentation.
        
        Args:
            tool_func: The tool function to register
            category: Tool category (database, connection, data, fts, help, admin)
        """
        doc = tool_func.__doc__ or ""
        # Parse docstring for name, description, and parameters
        lines = [line.strip() for line in doc.split('\n') if line.strip()]
        name = tool_func.__name__
        description = lines[0] if lines else "No description available"
        
        # Parse parameters
        params = {}
        in_params = False
        for line in lines[1:]:
            if line.lower().startswith('args:'):
                in_params = True
                continue
            if in_params and ':' in line:
                param, desc = line.split(':', 1)
                params[param.strip()] = desc.strip()
        
        cls._tools[name] = {
            'name': name,
            'description': description,
            'parameters': params,
            'function': tool_func,
            'category': category.lower()
        }
        return tool_func

def register_tools(mcp):
    """Register all help tools with the MCP server."""
    mcp.tool()(list_tools)
    mcp.tool()(get_tool_help)
    mcp.tool()(get_quick_start)
    
    logger.info("Registered Help tools")

# Help commands
@HelpSystem.register_tool(category='help')
@mcp_tool()
async def list_tools(category: str = None) -> Dict[str, Any]:
    """List all available MCP tools.
    
    Args:
        category: Optional category filter (database, calibre, help, admin)
        
    Returns:
        Dictionary of tool categories and their tools
    """
    if category and category.lower() in HelpSystem._categories:
        return {
            'status': 'success',
            'category': category,
            'tools': {
                name: tool['description'] 
                for name, tool in HelpSystem._tools.items()
                if tool.get('category', '').lower() == category.lower()
            }
        }
    
    # Return all tools grouped by category
    tools_by_category = {cat: {} for cat in HelpSystem._categories}
    
    for name, tool in HelpSystem._tools.items():
        cat = tool.get('category', 'database')
        if cat not in tools_by_category:
            tools_by_category[cat] = {}
        tools_by_category[cat][name] = tool['description']
    
    return {
        'status': 'success',
        'categories': {
            cat: len(tools)
            for cat, tools in tools_by_category.items()
            if tools  # Only include non-empty categories
        },
        'tools': tools_by_category
    }

@HelpSystem.register_tool(category='help')
@mcp_tool()
async def get_tool_help(tool_name: str) -> Dict[str, Any]:
    """Get detailed help for a specific tool.
    
    Args:
        tool_name: Name of the tool to get help for
        
    Returns:
        Detailed documentation including parameters, return types, and examples
    """
    tool = TOOL_REGISTRY.get(tool_name)
    if not tool:
        available = ", ".join(TOOL_REGISTRY.keys())
        return {
            "error": f"Tool '{tool_name}' not found. Available tools: {available}",
            "available_tools": list(TOOL_REGISTRY.keys())
        }
    return tool

@mcp_tool()
async def get_quick_start() -> str:
    """Get a quick start guide for using the MCP tools."""
    return {
        "quick_start": [
            "1. List available tools: `list_tools()`",
            "2. Get help for a tool: `get_tool_help('tool_name')`",
            "3. Initialize a database: `init_database('sqlite', {'database': 'mydb.sqlite'})`",
            "4. Execute a query: `execute_query('SELECT * FROM mytable')`"
        ],
        "example_workflows": [
            "Initialize and query SQLite:",
            "1. init_database('sqlite', {'database': 'test.db'})",
            "2. execute_query('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)')",
            "3. execute_query('INSERT INTO users (name) VALUES (?)', ['Alice'])",
            "4. execute_query('SELECT * FROM users')"
        ]
    }
