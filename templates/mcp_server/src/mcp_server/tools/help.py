"""
MCP Help Tool

This module provides a comprehensive help system for the MCP server, allowing users to
discover and understand available tools, their parameters, and usage examples.
"""

import re
import textwrap
from enum import Enum
from inspect import Parameter, signature
from typing import Any, Dict, List, Optional, Type

from mcp import tool
from mcp_server.tools import get_all_tools

# Maximum line width for help text (for better readability)
MAX_LINE_WIDTH = 80

# Regular expression to match type annotations like 'Optional[str]' or 'List[int]'
TYPE_ANNOTATION_PATTERN = re.compile(
    r"^([a-zA-Z_][a-zA-Z0-9_]*\.)*([a-zA-Z_][a-zA-Z0-9_]*)(\[.*\])?$"
)

# Global help text template
HELP_TEMPLATE = """
{name}
{underline}

{description}

{usage}

Parameters:
{parameters}

Returns:
{returns}

Examples:
{examples}
"""


def format_type_name(type_obj: Type) -> str:
    """Format a type object as a string, handling common cases nicely."""
    if type_obj is type(None):  # noqa: E721
        return "None"
    if hasattr(type_obj, "__origin__"):
        # Handle generic types like List, Dict, Optional, etc.
        origin = type_obj.__origin__
        if origin is list or origin is List:
            args = type_obj.__args__
            if args and len(args) == 1:
                return f"List[{format_type_name(args[0])}]"
            return "List"
        elif origin is dict or origin is Dict:
            args = type_obj.__args__
            if args and len(args) == 2:
                return f"Dict[{format_type_name(args[0])}, {format_type_name(args[1])}]"
            return "Dict"
        elif origin is type(Optional):
            args = type_obj.__args__
            if args and len(args) == 2 and args[1] is type(None):  # noqa: E721
                return f"Optional[{format_type_name(args[0])}]"
            return "Optional"

        # Handle other generic types
        name = getattr(origin, "__name__", str(origin))
        if hasattr(type_obj, "__args__"):
            args = ", ".join(format_type_name(arg) for arg in type_obj.__args__)
            return f"{name}[{args}]"
        return name

    # Handle Enum types
    if isinstance(type_obj, type) and issubclass(type_obj, Enum):
        values = [f'"{e.value}"' for e in type_obj]
        return "|".join(values)

    # Handle regular types
    return type_obj.__name__


def format_parameter_doc(param_name: str, param: Parameter, default: Any = Parameter.empty) -> str:
    """Format a parameter's documentation with its type and default value."""
    # Get type annotation
    param_type = "Any"
    if param.annotation != Parameter.empty:
        param_type = format_type_name(param.annotation)

    # Format the parameter line
    param_line = f"{param_name}: {param_type}"

    # Add default value if present
    if default != Parameter.empty:
        default_str = f"{default!r}" if not isinstance(default, str) else f"'{default}'"
        param_line += f" = {default_str}"

    # Add parameter kind indicator
    if param.kind == Parameter.POSITIONAL_ONLY:
        param_line = f"{param_line} (positional only)"
    elif param.kind == Parameter.POSITIONAL_OR_KEYWORD:
        if param.default == Parameter.empty:
            param_line = f"{param_line} (required)"
    elif param.kind == Parameter.VAR_POSITIONAL:
        param_line = f"*{param_line}"
    elif param.kind == Parameter.KEYWORD_ONLY:
        param_line = f"**{param_line}"
    elif param.kind == Parameter.VAR_KEYWORD:
        param_line = f"**{param_line}"

    return param_line


def get_tool_documentation(tool_func: callable) -> Dict[str, Any]:
    """Generate documentation for a tool function."""
    # Get the function signature
    sig = signature(tool_func)

    # Get the function's docstring and parse it
    docstring = tool_func.__doc__ or ""
    doc_lines = [line.strip() for line in docstring.split("\n") if line.strip()]

    # Extract description (first paragraph)
    description_lines = []
    for line in doc_lines:
        if not line.strip():
            break
        description_lines.append(line)

    description = "\n".join(description_lines)

    # Extract parameters section
    params_section = []
    param_docs = {}
    current_param = None

    for line in doc_lines[len(description_lines) :]:
        line = line.strip()
        if line.startswith(":"):
            if "param" in line or "type" in line or "return" in line or "rtype" in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    if key.startswith("param "):
                        param_name = key[6:].strip()
                        current_param = param_name
                        param_docs[param_name] = {"desc": value}
                    elif key.startswith("type ") and current_param:
                        param_name = key[5:].strip()
                        if param_name in param_docs:
                            param_docs[param_name]["type"] = value
                        current_param = None
                    elif key == "return":
                        returns = value
                    elif key == "rtype":
                        return_type = value
        elif current_param and line and line[0].isspace():
            # Continuation of parameter description
            if "desc" in param_docs[current_param]:
                param_docs[current_param]["desc"] += " " + line.strip()

    # Format parameters
    parameters = []
    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue

        param_info = param_docs.get(param_name, {})
        param_desc = param_info.get("desc", "No description available.")

        # Format the parameter line
        param_line = format_parameter_doc(param_name, param, param.default)

        # Add the description
        param_doc = f"  {param_line}\n"

        # Add the parameter description, properly indented and wrapped
        desc_lines = textwrap.wrap(
            param_desc,
            width=MAX_LINE_WIDTH - 6,  # Account for indentation
            initial_indent="    ",
            subsequent_indent="    ",
        )
        param_doc += "\n".join(desc_lines) + "\n"
        parameters.append(param_doc)

    # Format return value
    return_type = format_type_name(sig.return_annotation)
    returns = [f"  {return_type}"]

    # Add return description if available
    if "returns" in locals():
        return_desc = textwrap.wrap(
            returns, width=MAX_LINE_WIDTH - 4, initial_indent="  ", subsequent_indent="  "
        )
        returns.extend(return_desc)

    # Format usage examples
    examples = []
    in_example = False
    example_lines = []

    for line in doc_lines:
        if line.strip() == "Example:" or line.strip() == "Examples:":
            in_example = True
            continue

        if in_example:
            if line.strip() == "":
                if example_lines:
                    examples.append("  " + "\n  ".join(example_lines))
                    example_lines = []
                in_example = False
            else:
                example_lines.append(line.strip())

    if example_lines:
        examples.append("  " + "\n  ".join(example_lines))

    # If no examples found, add a default one
    if not examples:
        example_params = []
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            if param.default != Parameter.empty:
                example_params.append(f"{param_name}={param.default!r}")
            else:
                example_params.append(f"{param_name}=...")

        example = f"  result = await {tool_func.__name__}({', '.join(example_params)})"
        examples.append(example)

    # Build the full documentation
    tool_name = getattr(tool_func, "name", tool_func.__name__)

    doc = {
        "name": tool_name,
        "description": description,
        "parameters": "\n".join(parameters) if parameters else "  (No parameters)",
        "returns": "\n".join(returns),
        "examples": "\n".join(examples) if examples else "  (No examples provided)",
        "underline": "=" * len(tool_name) if tool_name else "",
    }

    # Generate usage string
    param_strs = []
    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue

        param_str = param_name
        if param.default != Parameter.empty:
            param_str = f"[{param_str}]"

        param_strs.append(param_str)

    doc["usage"] = f"Usage: {tool_name}({', '.join(param_strs)})"

    return doc


def format_tool_help(tool_func: callable) -> str:
    """Format the help text for a single tool."""
    doc = get_tool_documentation(tool_func)

    # Format the help text using the template
    help_text = HELP_TEMPLATE.format(
        name=doc["name"],
        underline=doc["underline"],
        description=doc["description"],
        usage=doc["usage"],
        parameters=doc["parameters"],
        returns=doc["returns"],
        examples=doc["examples"],
    )

    return help_text


def list_all_tools() -> List[Dict[str, Any]]:
    """List all available tools with their basic information."""
    tools = get_all_tools()
    tool_list = []

    for tool_name, tool_func in tools.items():
        docstring = tool_func.__doc__ or ""
        description = docstring.split("\n")[0] if docstring else "No description available."

        tool_list.append(
            {
                "name": tool_name,
                "description": description,
                "module": tool_func.__module__,
                "file": getattr(tool_func, "__code__", None) and tool_func.__code__.co_filename,
            }
        )

    return tool_list


def format_tool_list(tools: List[Dict[str, Any]]) -> str:
    """Format a list of tools for display."""
    if not tools:
        return "No tools available."

    # Sort tools by name
    tools = sorted(tools, key=lambda x: x["name"])

    # Find the maximum name length for alignment
    max_name_length = max(len(tool_info["name"]) for tool_info in tools) + 2  # +2 for padding

    # Build the tool list
    lines = ["Available Tools:", ""]

    for tool_info in tools:
        name = tool_info["name"].ljust(max_name_length)
        desc = tool_info["description"]
        lines.append(f"  {name} {desc}")

    return "\n".join(lines)


@tool(
    name="help",
    description="Get help about available tools and their usage.",
    parameters={
        "tool_name": {
            "type": "string",
            "description": (
                "Name of the tool to get help for. "
                "If not provided, lists all available tools."
            ),
            "required": False,
        },
        "search_term": {
            "type": "string",
            "description": "Search term to filter tools by name or description.",
            "required": False,
        },
    },
)
async def help_tool(tool_name: Optional[str] = None, search_term: Optional[str] = None) -> str:
    """
    Get help about available tools and their usage.

    This tool provides detailed documentation about the available tools in the MCP server,
    including their parameters, return values, and usage examples.

    Args:
        tool_name: Name of the tool to get help for. 
        If not provided, lists all available tools.
        search_term: Search term to filter tools by name or description.

    Returns:
        str: Formatted help text for the requested tool(s).

    Examples:
        # List all available tools
        help()

        # Get help for a specific tool
        help("help")

        # Search for tools containing a term
        help(search_term="file")
    """
    tools = get_all_tools()

    # If a tool name is provided, show help for that tool
    if tool_name:
        if tool_name not in tools:
            return f"Error: No tool named '{tool_name}' found."

        return format_tool_help(tools[tool_name])

    # If a search term is provided, filter tools by name or description
    if search_term:
        search_term = search_term.lower()
        filtered_tools = []

        for name, tool_func in tools.items():
            docstring = tool_func.__doc__ or ""
            description = docstring.split("\n")[0] if docstring else ""

            if (
                search_term in name.lower()
                or search_term in description.lower()
                or search_term in (tool_func.__doc__ or "").lower()
            ):
                filtered_tools.append(
                    {
                        "name": name,
                        "description": description,
                        "module": tool_func.__module__,
                        "file": getattr(tool_func, "__code__", None)
                        and tool_func.__code__.co_filename,
                    }
                )

        if not filtered_tools:
            return f"No tools found matching '{search_term}'."

        return format_tool_list(filtered_tools)

    # Otherwise, list all tools
    tool_list = [
        {
            "name": name,
            "description": (tool_func.__doc__ or "").split("\n")[0] if tool_func.__doc__ else "",
            "module": tool_func.__module__,
            "file": getattr(tool_func, "__code__", None) and tool_func.__code__.co_filename,
        }
        for name, tool_func in tools.items()
    ]

    return format_tool_list(tool_list)
