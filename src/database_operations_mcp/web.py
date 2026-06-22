"""FastAPI REST bridge for database-operations-mcp web_sota dashboard."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from fastapi import APIRouter, Query
from fastapi.responses import Response
from pydantic import BaseModel, Field

from database_operations_mcp.activity_log import (
    SortOrder,
    clear_logs,
    export_logs,
    get_activity,
    install_log_handler,
    log_activity,
    log_stats,
    query_logs,
)
from database_operations_mcp.chat import ChatService


class ChatRequest(BaseModel):
    message: str
    history: list[dict[str, str]] = []
    model: str | None = None
    personality: str | None = None
    session_id: str | None = None


class RefinePromptRequest(BaseModel):
    prompt: str
    model: str | None = None


logger = logging.getLogger(__name__)

PORTMANTEAU_TOOLS = {
    "db_connection",
    "db_operations",
    "db_schema",
    "db_management",
    "db_analyzer",
    "db_fts",
    "db_operations_extended",
    "help_system",
    "media_library",
    "windows_system",
    "calibre_integration",
    "system_init",
}

AGENTIC_TOOLS = {"agentic_workflow_tool", "database_agentic_assist"}


class ToolCallRequest(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


def _serialize_tool_result(result: Any) -> Any:
    if result is None:
        return None
    structured = getattr(result, "structured_content", None)
    if structured is not None:
        return structured
    content = getattr(result, "content", None)
    if content:
        texts = []
        for block in content:
            text = getattr(block, "text", None)
            if text:
                texts.append(text)
        if len(texts) == 1:
            try:
                return json.loads(texts[0])
            except json.JSONDecodeError:
                return texts[0]
        if texts:
            return texts
    if isinstance(result, dict):
        return result
    return str(result)


async def _list_mcp_tools(mcp_app) -> list[dict[str, Any]]:
    tools = await mcp_app.list_tools()
    return [
        {
            "name": tool.name,
            "description": tool.description,
            "inputSchema": getattr(tool, "inputSchema", None) or getattr(tool, "parameters", None),
        }
        for tool in tools
    ]


async def _build_capabilities(mcp_app) -> dict[str, Any]:
    tools = await mcp_app.list_tools()
    tool_names = [t.name for t in tools]
    portmanteau = [n for n in tool_names if n in PORTMANTEAU_TOOLS]
    atomic = [n for n in tool_names if n not in PORTMANTEAU_TOOLS]

    prompt_names: list[str] = []
    resource_uris: list[str] = []
    skill_uris: list[str] = []
    try:
        prompts = await mcp_app.list_prompts()
        prompt_names = [p.name for p in prompts]
    except Exception:
        logger.warning("Failed to list prompts")
    try:
        resources = await mcp_app.list_resources()
        resource_uris = [str(r.uri) for r in resources]
    except Exception:
        logger.warning("Failed to list resources")
    try:
        if hasattr(mcp_app, "list_skills"):
            skills = await mcp_app.list_skills()
            skill_uris = [str(s.uri) for s in skills]
    except Exception:
        logger.warning("Failed to list skills")

    sampling_tools = [n for n in tool_names if "agentic" in n.lower() or "assist" in n.lower()]
    agentic = [n for n in tool_names if n in AGENTIC_TOOLS or "agentic" in n.lower()]

    version = getattr(mcp_app, "version", None) or "1.4.1"

    return {
        "status": "ok",
        "fastmcp": str(version),
        "tool_surface": {
            "total": len(tool_names),
            "portmanteau_count": len(portmanteau),
            "atomic_count": len(atomic),
            "portmanteau_tools": portmanteau,
            "atomic_tools": atomic,
        },
        "prompts": {
            "available": len(prompt_names) > 0,
            "count": len(prompt_names),
            "names": prompt_names,
        },
        "resources": {
            "available": len(resource_uris) > 0,
            "count": len(resource_uris),
            "uris": resource_uris[:50],
        },
        "skills": {
            "available": len(skill_uris) > 0,
            "count": len(skill_uris),
            "uris": skill_uris[:50],
        },
        "sampling": {
            "available": len(sampling_tools) > 0,
            "indicator_tools": sampling_tools,
        },
        "agentic_workflows": {
            "available": len(agentic) > 0,
            "tools": agentic,
        },
    }


router = APIRouter(prefix="/api")


def setup_webapp(app, mcp_app=None) -> None:
    install_log_handler()
    chat_service = ChatService()

    if not mcp_app:
        app.include_router(router)
        return

    @router.get("/health")
    async def api_health():
        return {"status": "ok", "mcp": "database-operations-mcp"}

    @router.get("/llm/providers")
    async def get_llm_providers():
        import httpx

        ollama_models = []
        lm_studio_models = []

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:11434/api/tags", timeout=2.0)
                if response.status_code == 200:
                    data = response.json()
                    ollama_models = [{"name": m["name"]} for m in data.get("models", [])]
        except Exception as e:
            err_msg = f"{type(e).__name__}: {e}" if str(e) else type(e).__name__
            logger.debug(f"Ollama discovery failed: {err_msg}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:1234/v1/models", timeout=2.0)
                if response.status_code == 200:
                    data = response.json()
                    lm_studio_models = [{"name": m["id"]} for m in data.get("data", [])]
        except Exception as e:
            err_msg = f"{type(e).__name__}: {e}" if str(e) else type(e).__name__
            logger.debug(f"LM Studio discovery failed: {err_msg}")

        return {
            "ollama": ollama_models,
            "lm_studio": lm_studio_models,
        }

    @router.get("/capabilities")
    async def api_capabilities():
        return await _build_capabilities(mcp_app)

    @router.get("/tools")
    async def list_tools():
        return {"tools": await _list_mcp_tools(mcp_app)}

    @router.post("/tools/call")
    async def call_tool_endpoint(request: ToolCallRequest):
        try:
            result = await mcp_app.call_tool(request.name, request.arguments)
            payload = _serialize_tool_result(result)
            is_error = isinstance(payload, dict) and payload.get("success") is False
            log_activity(
                "tool_call",
                f"{request.name} ({'error' if is_error else 'ok'})",
                level="ERROR" if is_error else "INFO",
                meta={"tool": request.name, "arguments": request.arguments},
            )
            return {"result": payload, "isError": is_error}
        except Exception as exc:
            log_activity(
                "tool_call",
                f"{request.name} (exception)",
                level="ERROR",
                meta={"error": str(exc)},
            )
            return {"result": {"success": False, "error": str(exc)}, "isError": True}

    @router.get("/activity")
    async def activity_feed(limit: int = Query(50, ge=1, le=200)):
        return {"entries": get_activity(limit)}

    @router.delete("/activity")
    async def activity_clear():
        clear_logs()
        return {"success": True}

    @router.get("/logs")
    async def logs_query(
        limit: int = Query(50, ge=1, le=500),
        offset: int = Query(0, ge=0),
        level: str | None = Query(None),
        kind: str | None = Query(None),
        search: str | None = Query(None),
        sort: str = Query("desc"),
        after_id: str | None = Query(None),
    ):
        order: SortOrder = "asc" if sort == "asc" else "desc"
        return query_logs(
            limit=limit,
            offset=offset,
            level=level,
            kind=kind,
            search=search,
            sort=order,
            after_id=after_id,
        )

    @router.get("/logs/stats")
    async def logs_stats():
        return log_stats()

    @router.get("/logs/export")
    async def logs_export(
        fmt: str = Query("json", alias="format"),
        level: str | None = Query(None),
        kind: str | None = Query(None),
        search: str | None = Query(None),
        sort: str = Query("desc"),
    ):
        order: SortOrder = "asc" if sort == "asc" else "desc"
        export_format = fmt if fmt in ("json", "csv") else "json"
        body, media_type, filename = export_logs(
            fmt=export_format,
            level=level,
            kind=kind,
            search=search,
            sort=order,
        )
        return Response(
            content=body,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    @router.delete("/logs")
    async def logs_clear():
        clear_logs()
        log_activity("system", "Log buffer cleared", level="WARNING")
        return {"success": True}

    @router.post("/v1/chat")
    async def chat_interaction(request: ChatRequest):
        return await chat_service.ask(request)

    @router.post("/v1/chat/refine")
    async def refine_prompt(request: RefinePromptRequest):
        return {"refined": request.prompt}

    @router.get("/v1/settings/llm")
    async def get_llm_settings():
        return {
            "provider": "ollama",
            "model": "gemma4:e4b",
            "endpoint": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        }

    app.include_router(router)
