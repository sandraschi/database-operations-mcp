"""
Web SOTA backend: FastAPI app with FastMCP 3.1 universal gateway.

- Mounts the Database Operations MCP server at /mcp (same process).
- REST bridge: GET /api/tools, POST /api/tools/call (in-process Client(mcp)).
Reservoir port: 10709 (see web_sota/start.ps1).
"""

import logging
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Register all tools on the global MCP instance before creating http_app
from database_operations_mcp.config.mcp_config import get_mcp
from database_operations_mcp.main import DatabaseOperationsMCP

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Ensure all tools are registered (side effect of constructor)
DatabaseOperationsMCP()
mcp = get_mcp()

# FastMCP 3.1: ASGI app for MCP over HTTP
mcp_app = mcp.http_app(path="/")

# FastAPI app with MCP lifespan (required for session management)
app = FastAPI(
    title="Database Operations MCP Web SOTA Backend",
    version="0.1.0",
    lifespan=mcp_app.lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:10708", "http://localhost:10708"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount MCP at /mcp (universal gateway: same process serves REST + MCP)
app.mount("/mcp", mcp_app)


# REST bridge: in-process client (no HTTP to self)
class ToolCallRequest(BaseModel):
    name: str
    arguments: dict[str, Any] = {}


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "mcp": "mounted"}


@app.get("/api/health")
def api_health() -> dict:
    return {"status": "ok", "mcp": "mounted"}


@app.get("/")
def root() -> dict:
    return {"service": "database-operations-mcp-web-sota-backend", "mcp_path": "/mcp"}


@app.get("/api/tools")
async def list_tools() -> dict:
    """List tools from the in-process MCP server."""
    try:
        from fastmcp.client import Client

        async with Client(mcp) as client:
            tools = await client.list_tools()
            return {
                "tools": [
                    {
                        "name": t.name,
                        "description": getattr(t, "description", None) or "",
                        "inputSchema": getattr(t, "inputSchema", None),
                    }
                    for t in tools
                ]
            }
    except Exception as e:
        logger.exception("list_tools failed")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/capabilities")
async def capabilities() -> dict:
    """Expose webapp-friendly FastMCP capability summary."""
    try:
        from fastmcp.client import Client

        async with Client(mcp) as client:
            tools = await client.list_tools()
            tool_names = [t.name for t in tools]

            prompt_names: list[str] = []
            resource_uris: list[str] = []

            try:
                prompts = await client.list_prompts()
                prompt_names = [getattr(p, "name", "") for p in prompts if getattr(p, "name", "")]
            except Exception:
                prompt_names = []

            try:
                resources = await client.list_resources()
                resource_uris = [
                    getattr(r, "uri", "")
                    for r in resources
                    if getattr(r, "uri", "")
                ]
            except Exception:
                resource_uris = []

            portmanteau_roots = {
                "db_connection",
                "db_operations",
                "db_schema",
                "db_management",
                "db_fts",
                "db_analyzer",
                "db_operations_extended",
                "browser_bookmarks",
                "media_library",
                "windows_system",
                "help_system",
                "chrome_profiles",
                "firefox_profiles",
                "firefox_curated",
                "firefox_tagging",
                "firefox_backup",
                "firefox_utils",
                "system_init",
                "sync_tools",
            }
            portmanteau_tools = [name for name in tool_names if name in portmanteau_roots]
            atomic_tools = [name for name in tool_names if name not in portmanteau_roots]
            agentic_tools = [name for name in tool_names if "agentic" in name.lower()]
            workflow_tools = [
                name
                for name in tool_names
                if "workflow" in name.lower() or "assistant" in name.lower()
            ]
            skill_resources = [uri for uri in resource_uris if str(uri).startswith("skill://")]

            return {
                "status": "ok",
                "fastmcp": "3.1+",
                "tool_surface": {
                    "total": len(tool_names),
                    "portmanteau_count": len(portmanteau_tools),
                    "atomic_count": len(atomic_tools),
                    "portmanteau_tools": portmanteau_tools,
                    "atomic_tools": atomic_tools,
                },
                "prompts": {
                    "available": len(prompt_names) > 0,
                    "count": len(prompt_names),
                    "names": prompt_names,
                },
                "resources": {
                    "available": len(resource_uris) > 0,
                    "count": len(resource_uris),
                    "uris": resource_uris,
                },
                "skills": {
                    "available": len(skill_resources) > 0,
                    "count": len(skill_resources),
                    "uris": skill_resources,
                },
                "sampling": {
                    "available": len(agentic_tools) > 0,
                    "indicator_tools": agentic_tools,
                },
                "agentic_workflows": {
                    "available": len(workflow_tools) > 0,
                    "tools": workflow_tools,
                },
            }
    except Exception as e:
        logger.exception("capabilities failed")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/tools/call")
async def call_tool(body: ToolCallRequest) -> dict:
    """Call a tool by name with arguments (in-process)."""
    try:
        from fastmcp.client import Client

        async with Client(mcp) as client:
            result = await client.call_tool(body.name, body.arguments)
            return {
                "result": result.data if hasattr(result, "data") else result,
                "isError": getattr(result, "is_error", getattr(result, "isError", False)),
            }
    except Exception as e:
        from fastmcp.exceptions import ToolError

        if isinstance(e, ToolError):
            logger.warning("call_tool validation or tool error: %s", e)
            raise HTTPException(status_code=400, detail=str(e)) from e
        logger.exception("call_tool failed")
        raise HTTPException(status_code=500, detail=str(e)) from e
