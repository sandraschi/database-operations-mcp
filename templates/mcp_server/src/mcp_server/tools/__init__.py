"""
MCP Server Tools Package

This package contains all the tools available in the MCP server.
Tools are automatically discovered and registered when the server starts.
"""

import importlib
import pkgutil
from pathlib import Path
from typing import Dict, Optional, Type

from mcp import Tool

# Dictionary to store all registered tools
TOOLS: Dict[str, Type[Tool]] = {}


def register_tool(tool_cls: Type[Tool]) -> Type[Tool]:
    """
    Decorator to register a tool class.

    Args:
        tool_cls: The tool class to register

    Returns:
        The same tool class for chaining
    """
    if not hasattr(tool_cls, "name"):
        raise ValueError("Tool class must have a 'name' attribute")

    if not hasattr(tool_cls, "description"):
        raise ValueError("Tool class must have a 'description' attribute")

    TOOLS[tool_cls.name] = tool_cls
    return tool_cls


def discover_tools() -> None:
    """
    Discover and import all tools in this package.
    This function should be called when the server starts.
    """
    # Get the directory containing this file
    package_dir = Path(__file__).parent

    # Import all modules in this directory
    for _, module_name, _ in pkgutil.iter_modules([str(package_dir)]):
        if module_name == "__init__" or module_name.startswith("_"):
            continue

        try:
            importlib.import_module(f".{module_name}", package=__name__)
        except ImportError as e:
            print(f"Error importing tool module {module_name}: {e}")


def get_tool(name: str) -> Optional[Type[Tool]]:
    """
    Get a tool class by name.

    Args:
        name: The name of the tool to get

    Returns:
        The tool class, or None if not found
    """
    return TOOLS.get(name)


def get_all_tools() -> Dict[str, Type[Tool]]:
    """
    Get all registered tools.

    Returns:
        A dictionary mapping tool names to tool classes
    """
    return TOOLS.copy()
