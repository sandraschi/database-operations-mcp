"""
MCP Help Tool

This module provides a help system for the MCP server, allowing users to discover
and understand available tools and their usage.
"""

import re
from enum import Enum
from inspect import Parameter
from typing import Any, Dict, List, Optional, Type

# Maximum line width for help text (for better readability)
MAX_LINE_WIDTH = 80

# Regular expression to match type annotations like 'Optional[str]' or 'List[int]'
TYPE_ANNOTATION_PATTERN = re.compile(
    r"^([a-zA-Z_][a-zA-Z0-9_]*\.)*([a-zA-Z_][a-zA-Z0-9_]*)(\[.*\])?$"
)


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
        return f"{'|'.join(f'"{e.value}"' for e in type_obj)}"

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
        default_str = f"'{default}'"
