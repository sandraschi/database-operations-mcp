"""FastAPI web bridge — REST /api/* for web_sota (ports 10708/10709)."""

from __future__ import annotations

import importlib
import logging
import os
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database_operations_mcp.config.mcp_config import get_mcp
from database_operations_mcp.web import setup_webapp

logger = logging.getLogger(__name__)


def load_tools() -> None:
    """Import tool modules so @mcp.tool decorators register."""
    from database_operations_mcp.tools import (  # noqa: F401
        agentic_tools,
        calibre_integration,
        db_analyzer,
        db_connection,
        db_fts,
        db_management,
        db_operations,
        db_operations_extended,
        db_schema,
        help_system,
        media_library,
        system_init,
        test_tool,
        windows_system,
    )

    if os.getenv("ENABLE_ATOMIC_DB_TOOLS", "true").lower() == "true":
        importlib.import_module("database_operations_mcp.tools.db_atomic")

    from database_operations_mcp import prompts  # noqa: F401


def build_web_app() -> FastAPI:
    mcp = get_mcp()
    load_tools()

    app = FastAPI(title="database-operations-mcp")

    cors_origins = os.environ.get("CORS_ORIGINS", "*")
    cors_origins_list = [o.strip() for o in cors_origins.split(",") if o.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health():
        return {"status": "ok", "server": "database-operations-mcp"}

    setup_webapp(app, mcp_app=mcp)
    log_activity_on_boot()
    return app


def log_activity_on_boot() -> None:
    from database_operations_mcp.activity_log import log_activity

    log_activity("system", "Web bridge started", level="INFO")


web_app = build_web_app()


def run_http_web() -> int:
    port = int(os.getenv("MCP_PORT", "10709"))
    host = os.getenv("MCP_HOST", "127.0.0.1")
    for index, arg in enumerate(sys.argv):
        if arg == "--port" and index + 1 < len(sys.argv):
            try:
                port = int(sys.argv[index + 1])
            except ValueError:
                pass
        if arg.startswith("--port="):
            try:
                port = int(arg.split("=", 1)[1])
            except ValueError:
                pass

    logger.info("Starting database-operations-mcp web bridge on %s:%s", host, port)
    uvicorn.run(web_app, host=host, port=port, log_level="info")
    return 0
