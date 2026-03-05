"""
MCP Prompts (FastMCP 3.1).

Prompts are reusable, parameterized message templates. Clients can request them
and inject the returned messages into the conversation. Importing this package
registers the prompts with the global MCP instance.
"""

from database_operations_mcp.prompts import database_prompts  # noqa: F401 - register @mcp.prompt
