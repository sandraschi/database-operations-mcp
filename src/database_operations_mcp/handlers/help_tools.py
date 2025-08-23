"""
Help system for Database Operations MCP.

Provides interactive help and documentation for all available tools.
"""

from typing import Dict, List, Optional, Any, TYPE_CHECKING, Callable
import inspect
import json
from pathlib import Path

if TYPE_CHECKING:
    from fastmcp import FastMCP

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
    def register_tool(cls, tool_func=None, *, category: str = 'database'):
        """Register a tool with its help documentation.
        
        Can be used as a decorator with or without parameters:
            @HelpSystem.register_tool
            @HelpSystem.register_tool(category='database')
            
        Args:
            tool_func: The tool function to register (used internally)
            category: Tool category (database, connection, data, fts, help, admin)
        """
        def decorator(func):
            doc = func.__doc__ or ""
            # Parse docstring for name, description, and parameters
            lines = [line.strip() for line in doc.split('\n') if line.strip()]
            name = func.__name__
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
                'function': func,
                'category': category.lower()
            }
            return func
            
        # Handle both @register_tool and @register_tool()
        if tool_func is None:
            return decorator
        return decorator(tool_func)

def register_tools(mcp):
    """Register all help tools with the MCP server."""
    @mcp.tool()
    @HelpSystem.register_tool
    async def list_tools(category: str = None) -> Dict[str, Any]:
        """List all available MCP tools.
        
        Args:
            category: Optional category filter (database, calibre, help, admin)
            
        Returns:
            Dictionary of tool categories and their tools
        """
        if category:
            return {k: v for k, v in HelpSystem._tools.items() if v.get('category') == category}
        return HelpSystem._tools

    @mcp.tool()
    @HelpSystem.register_tool
    async def get_tool_help(tool_name: str) -> Dict[str, Any]:
        """Get detailed help for a specific tool.
        
        Args:
            tool_name: Name of the tool to get help for
            
        Returns:
            Detailed documentation including parameters, return types, and examples
        """
        tool = HelpSystem._tools.get(tool_name)
        if not tool:
            return {"error": f"No help available for tool: {tool_name}"}
        return tool

    @mcp.tool()
    @HelpSystem.register_tool
    async def get_quick_start() -> Dict[str, Any]:
        """Get a quick start guide for using the MCP tools."""
        return {
            "title": "Database Operations MCP - Quick Start",
            "sections": [
                {
                    "title": "Connecting to a Database",
                    "commands": [
                        "connect --type postgres --host localhost --port 5432 --database mydb --username user"
                    ]
                },
                {
                    "title": "Basic Queries",
                    "commands": [
                        "list_tables",
                        "describe_table --table users"
                    ]
                }
            ]
        }

    return mcp
