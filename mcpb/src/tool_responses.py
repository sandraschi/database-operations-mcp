"""Standard MCP tool response helpers for agents and static tool analyzers.

All portmanteau tools should return dicts that include, on failure:
success, message, error, error_type, and optionally recovery_options and retryable.
"""

from __future__ import annotations

from typing import Any, Literal

ErrorType = Literal["fatal", "retryable", "user_fixable", "invalid_input"]

# Documented envelope (also described in tool docstrings):
# Success: { "success": True, "message": str, ... operation-specific keys ... }
# Failure: { "success": False, "message": str, "error": str, "error_type": ErrorType,
#            "retryable": bool, "recovery_options": list[str] | None, ... }


def mcp_error(
    *,
    message: str,
    error: str | None = None,
    error_type: ErrorType = "fatal",
    recovery_options: list[str] | None = None,
    retryable: bool = False,
    **extra: Any,
) -> dict[str, Any]:
    """Build a consistent error dict for MCP tools."""
    out: dict[str, Any] = {
        "success": False,
        "message": message,
        "error": error if error is not None else message,
        "error_type": error_type,
        "retryable": retryable,
    }
    if recovery_options:
        out["recovery_options"] = recovery_options
    out.update(extra)
    return out


def unknown_operation_response(
    operation: str,
    available_operations: list[str],
    *,
    extra_recovery: list[str] | None = None,
) -> dict[str, Any]:
    """Standard response for an invalid `operation` string."""
    recovery = [
        "Use exactly one of the values in `available_operations` for the `operation` parameter.",
        "Call help_system(operation='tool_help', tool_name='<this_tool>') for full documentation.",
    ]
    if extra_recovery:
        recovery.extend(extra_recovery)
    return mcp_error(
        message=f"Unknown operation: {operation}",
        error=f"Unknown operation: {operation}",
        error_type="invalid_input",
        recovery_options=recovery,
        retryable=False,
        operation=operation,
        available_operations=available_operations,
    )


def connection_not_found(connection_name: str) -> dict[str, Any]:
    """Registered connection missing (user-fixable)."""
    return mcp_error(
        message=f"Connection not registered: {connection_name}",
        error=f"No connector registered for connection_name={connection_name!r}",
        error_type="user_fixable",
        recovery_options=[
            "Register the connection with db_connection(operation='register', ...).",
            "List existing names with db_connection(operation='list').",
        ],
        retryable=False,
        connection_name=connection_name,
    )
