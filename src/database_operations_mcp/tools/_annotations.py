"""Shared MCP tool-annotation constants.

Real MCP protocol fields (mcp.types.ToolAnnotations), not the placeholder
{"readonly": True} shape shown in mcp-central-docs/standards/TOOL_DESIGN_STANDARDS.md
section 9 -- that key does not exist on ToolAnnotations and is silently dropped
as unvalidated extra_data. FastMCP accepts a plain dict here and coerces it to
ToolAnnotations, so these are ordinary dicts using the real field names.

Per TOOL_DESIGN_STANDARDS.md section 9:
- READ_ONLY: tool does not mutate state (queries, list, get status).
- MUTATING: tool changes state but does not destroy (create, update, configure).
- DESTRUCTIVE: tool may delete, overwrite, or irreversibly change data. Applied
  to portmanteau tools if ANY of their sub-operations can delete/drop/reset,
  even when most of their operations are read-only -- the annotation reflects
  worst-case risk exposure of invoking the tool, not the common case.
"""

READ_ONLY = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
MUTATING = {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False}
DESTRUCTIVE = {"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False}
