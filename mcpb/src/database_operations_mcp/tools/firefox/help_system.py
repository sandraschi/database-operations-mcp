"""Help system for Firefox bookmark tools."""

from collections.abc import Callable
from typing import Any, Optional


class HelpSystem:
    """Manages help documentation for tools."""

    _instance: Optional["HelpSystem"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools: dict[str, dict[str, Any]] = {}
        return cls._instance

    @classmethod
    def register_tool(cls, category: str = "general") -> Callable:
        """Decorator to register a tool with help documentation.

        Args:
            category: Category for the tool (e.g., 'firefox', 'bookmarks')

        Returns:
            Decorator function
        """

        def decorator(func: Callable) -> Callable:
            # Get or create help entry for this tool
            help_entry = {
                "name": func.__name__,
                "doc": func.__doc__ or "No documentation available.",
                "category": category,
                "function": func,
            }

            # Store the help entry
            cls()._tools[func.__name__] = help_entry
            return func

        return decorator

    @classmethod
    def get_help(cls, tool_name: str) -> dict[str, Any] | None:
        """Get help information for a specific tool.

        Args:
            tool_name: Name of the tool to get help for

        Returns:
            Dictionary containing help information or None if not found
        """
        return cls()._tools.get(tool_name)

    @classmethod
    def list_tools(cls, category: str | None = None) -> dict[str, dict[str, Any]]:
        """List all registered tools, optionally filtered by category.

        Args:
            category: If provided, only return tools in this category

        Returns:
            Dictionary mapping tool names to their help entries
        """
        if category is None:
            return cls()._tools.copy()
        return {name: tool for name, tool in cls()._tools.items() if tool["category"] == category}
