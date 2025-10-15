"""
Tool Discovery Module

This module provides functionality to discover and load FastMCP 2.13 compliant tools.
"""

import importlib
import inspect
import pkgutil
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Type, TypeVar

# Import FastMCP types
try:
    from mcp.server import FastMCPServer, FastMCPTool
    from mcp.types import Tool, ToolCall, ToolDefinition, ToolError, ToolResult
    from mcp.utils.logging import get_logger
except ImportError:
    # Fallback for development
    from typing import Any, Callable, Dict, Optional, Type, TypedDict, TypeVar

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

    class FastMCPTool:
        def __init__(self, name: str, description: str, parameters: Dict[str, Any], func: Callable):
            self.name = name
            self.description = description
            self.parameters = parameters
            self.func = func

        async def __call__(self, **kwargs) -> Any:
            return await self.func(**kwargs)


logger = get_logger(__name__)

# Type variable for tool classes
T = TypeVar("T", bound=FastMCPTool)


def discover_tools(
    package_path: str = "mcp_server.tools",
    base_dir: Optional[Path] = None,
) -> Dict[str, Type[FastMCPTool]]:
    """Discover all FastMCP tools in the specified package.

    Args:
        package_path: The Python package path to search for tools.
        base_dir: The base directory of the package (for development).

    Returns:
        A dictionary mapping tool names to tool classes.
    """
    tools: Dict[str, Type[FastMCPTool]] = {}

    try:
        # Import the package
        package = importlib.import_module(package_path)

        # Get the package directory
        if base_dir is None:
            package_dir = Path(package.__file__).parent
        else:
            package_dir = base_dir / "src" / package_path.replace(".", "/")

        # Find all Python modules in the package
        for _, module_name, is_pkg in pkgutil.iter_modules([str(package_dir)]):
            if module_name.startswith("_") or module_name == "fastmcp_help":
                continue

            module_path = f"{package_path}.{module_name}"

            try:
                # Import the module
                module = importlib.import_module(module_path)

                # Find all FastMCPTool subclasses in the module
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (
                        issubclass(obj, FastMCPTool)
                        and obj != FastMCPTool
                        and obj.__module__ == module.__name__
                    ):
                        # Register the tool if it has a name
                        if hasattr(obj, "name") and obj.name:
                            tools[obj.name] = obj
                            logger.debug(f"Discovered tool: {obj.name} ({obj.__name__})")

            except ImportError as e:
                logger.warning(f"Failed to import module {module_path}: {e}")
                continue
            except Exception as e:
                logger.error(f"Error discovering tools in {module_path}: {e}", exc_info=True)
                continue

    except ImportError as e:
        logger.error(f"Failed to import package {package_path}: {e}")
    except Exception as e:
        logger.error(f"Error discovering tools: {e}", exc_info=True)

    return tools


def load_tool(
    tool_class: Type[FastMCPTool], server: FastMCPServer, *args: Any, **kwargs: Any
) -> Optional[FastMCPTool]:
    """Load a single tool.

    Args:
        tool_class: The tool class to instantiate.
        server: The FastMCP server instance.
        *args: Positional arguments to pass to the tool's constructor.
        **kwargs: Keyword arguments to pass to the tool's constructor.

    Returns:
        The instantiated tool, or None if loading failed.
    """
    try:
        # Check if the tool has a register_tool function
        if hasattr(tool_class, "register_tool") and callable(tool_class.register_tool):
            return tool_class.register_tool(server, *args, **kwargs)

        # Otherwise, try to instantiate the tool directly
        return tool_class(server, *args, **kwargs)

    except Exception as e:
        logger.error(f"Failed to load tool {tool_class.__name__}: {e}", exc_info=True)
        return None


def load_tools(
    tools: Dict[str, Type[FastMCPTool]], server: FastMCPServer, *args: Any, **kwargs: Any
) -> Dict[str, FastMCPTool]:
    """Load multiple tools.

    Args:
        tools: A dictionary mapping tool names to tool classes.
        server: The FastMCP server instance.
        *args: Positional arguments to pass to the tools' constructors.
        **kwargs: Keyword arguments to pass to the tools' constructors.

    Returns:
        A dictionary mapping tool names to instantiated tools.
    """
    loaded_tools: Dict[str, FastMCPTool] = {}

    for name, tool_class in tools.items():
        tool = load_tool(tool_class, server, *args, **kwargs)
        if tool:
            loaded_tools[name] = tool

    return loaded_tools


def register_tools(
    server: FastMCPServer,
    package_path: str = "mcp_server.tools",
    base_dir: Optional[Path] = None,
    *args: Any,
    **kwargs: Any,
) -> Dict[str, FastMCPTool]:
    """Discover and register all FastMCP tools.

    Args:
        server: The FastMCP server instance.
        package_path: The Python package path to search for tools.
        base_dir: The base directory of the package (for development).
        *args: Positional arguments to pass to the tools' constructors.
        **kwargs: Keyword arguments to pass to the tools' constructors.

    Returns:
        A dictionary mapping tool names to instantiated tools.
    """
    # Discover all tools
    tool_classes = discover_tools(package_path, base_dir)

    # Load and register the help tool first
    from mcp_server.tools.fastmcp_help import FastMCPHelpTool

    help_tool = FastMCPHelpTool(server)
    server.register_tool(help_tool)

    # Load and register all other tools
    loaded_tools = load_tools(tool_classes, server, *args, **kwargs)

    # Register all tools with the server
    for name, tool in loaded_tools.items():
        server.register_tool(tool)

    # Add the help tool to the result
    loaded_tools["help"] = help_tool

    return loaded_tools
