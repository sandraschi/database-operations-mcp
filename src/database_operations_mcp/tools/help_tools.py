"""
Help system for Database Operations MCP.
Provides interactive help and documentation for all available tools.
"""

from typing import Dict, Any, Optional, List, Callable, TypeVar, Union
import inspect
import re

# Import the global MCP instance
from database_operations_mcp.config.mcp_config import mcp

# Type variable for function type
F = TypeVar('F', bound=Callable[..., Any])

class HelpSystem:
    """Centralized help system for MCP tools."""
    
    _tools = {}
    _categories = {
        'database': 'Core database operations',
        'firefox': 'Firefox bookmark tools',
        'calibre': 'Calibre library tools',
        'registry': 'Windows Registry tools',
        'help': 'Help and documentation'
    }
    
    @classmethod
    def register_tool(cls, tool_func: Optional[F] = None, *, category: str = 'database') -> Union[Callable[[F], F], F]:
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
            description = doc.split('\n')[0] if doc else "No description"
            
            # Parse parameters from docstring
            params = {}
            param_section = re.search(r'Args:(.*?)(?=\n\w+:|\Z)', doc, re.DOTALL)
            if param_section:
                param_lines = [line.strip() for line in param_section.group(1).split('\n') if line.strip()]
                for line in param_lines:
                    if ':' in line:
                        param_name, param_desc = line.split(':', 1)
                        param_name = param_name.strip()
                        param_desc = param_desc.strip()
                        params[param_name] = param_desc
            
            # Store tool metadata
            cls._tools[name] = {
                'name': name,
                'description': description,
                'docstring': doc,
                'parameters': params,
                'category': category.lower()
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
            tools = {name: info for name, info in cls._tools.items() 
                    if info['category'] == category}
        else:
            tools = cls._tools
        
        # Group tools by category
        categorized = {}
        for tool_name, tool_info in tools.items():
            cat = tool_info['category']
            if cat not in categorized:
                categorized[cat] = {
                    'description': cls._categories.get(cat, 'Uncategorized'),
                    'tools': []
                }
            categorized[cat]['tools'].append({
                'name': tool_name,
                'description': tool_info['description']
            })
        
        return {
            'status': 'success',
            'categories': categorized,
            'total_tools': len(tools)
        }
    
    @classmethod
    def get_tool_help(cls, tool_name: str) -> Dict[str, Any]:
        """Get detailed help for a specific tool.
        
        Args:
            tool_name: Name of the tool to get help for
            
        Returns:
            Dictionary with detailed tool information
        """
        if tool_name not in cls._tools:
            return {
                'status': 'error',
                'error': f'Tool not found: {tool_name}'
            }
        
        tool_info = cls._tools[tool_name]
        return {
            'status': 'success',
            'tool': {
                'name': tool_info['name'],
                'description': tool_info['description'],
                'category': tool_info['category'],
                'category_description': cls._categories.get(tool_info['category'], ''),
                'parameters': tool_info['parameters'],
                'docstring': tool_info['docstring']
            }
        }

# Register tools using the @mcp.tool decorator
# The mcp instance is imported from the centralized config

@mcp.tool()
@HelpSystem.register_tool(category='help')
async def help(category: Optional[str] = None) -> Dict[str, Any]:
    """Get help for all available tools or filter by category.
    
    Args:
        category: Optional category to filter tools (e.g., 'database', 'registry')
        
    Returns:
        Dictionary with help information for all tools in the specified category
        or all tools if no category is specified.
    """
    return HelpSystem.get_help(category)

@mcp.tool()
@HelpSystem.register_tool(category='help')
async def tool_help(tool_name: str) -> Dict[str, Any]:
    """Get detailed help for a specific tool.
    
    Args:
        tool_name: Name of the tool to get help for
        
    Returns:
        Dictionary with detailed information about the specified tool
        including its description, parameters, and usage examples.
    """
    return HelpSystem.get_tool_help(tool_name)
