"""
Help system for Database Operations MCP.
Provides interactive help and documentation for all available tools.
"""

from typing import Dict, Any, Optional
import inspect
from fastmcp import tool

class HelpSystem:
    """Centralized help system for MCP tools."""
    
    _tools = {}
    _categories = {
        'database': 'Core database operations',
        'firefox': 'Firefox bookmark tools',
        'calibre': 'Calibre library tools',
        'help': 'Help and documentation'
    }
    
    @classmethod
    def register_tool(cls, tool_func=None, *, category: str = 'database'):
        """Register a tool with its documentation."""
        def decorator(func):
            doc = inspect.getdoc(func) or ""
            name = func.__name__
            description = doc.split('\n')[0] if doc else "No description"
            
            # Parse parameters
            params = {}
            sig = inspect.signature(func)
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                param_type = str(param.annotation)
                if param_type.startswith('typing.'):
                    param_type = param_type[7:]
                params[param_name] = {
                    'type': param_type,
                    'default': param.default if param.default != param.empty else None,
                    'required': param.default == param.empty
                }
            
            cls._tools[name] = {
                'name': name,
                'description': description,
                'parameters': params,
                'category': category.lower()
            }
            return func
            
        return decorator(tool_func) if tool_func else decorator

def register_tools(mcp):
    """Register help tools with the MCP server."""
    @mcp.tool()
    @HelpSystem.register_tool(category='help')
    async def list_tools(category: str = None) -> Dict[str, Any]:
        """List all available tools, optionally filtered by category.
        
        Args:
            category: Optional category to filter tools
        """
        if category:
            return {
                cat: [t for t in tools if t['category'] == category]
                for cat, tools in HelpSystem._tools.items()
            }
        return HelpSystem._tools

    @mcp.tool()
    @HelpSystem.register_tool(category='help')
    async def get_help(tool_name: str) -> Dict[str, Any]:
        """Get detailed help for a specific tool.
        
        Args:
            tool_name: Name of the tool to get help for
        """
        return HelpSystem._tools.get(tool_name, {"error": "Tool not found"})

    return mcp