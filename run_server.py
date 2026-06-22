"""PyInstaller entry point — dual transport."""
import _datetime  # noqa: F401 -- eager import stdlib C extensions
import _strptime  # noqa: F401 -- eager import stdlib C extensions
import mcp.types  # noqa: F401 -- eager bootstrap mcp types

import os
import sys

# Setup extraction path
if getattr(sys, "frozen", False):
    _extract_root = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    _src = os.path.join(_extract_root, "src")
    for _p in [_extract_root, _src]:
        if _p not in sys.path:
            sys.path.insert(0, _p)
else:
    sys.path.insert(0, "src")

# Configure default CORS origins environment variable for the backend
_tauri_port = os.environ.get("PORT", "10709")
os.environ.setdefault(
    "CORS_ORIGINS",
    f"http://127.0.0.1:{_tauri_port},http://localhost:{_tauri_port},"
    "tauri://localhost,http://tauri.localhost,https://tauri.localhost,null",
)

from database_operations_mcp.http_app import run_http_web

if __name__ == "__main__":
    port = os.environ.get("PORT") or os.environ.get("MCP_PORT")
    if port:
        os.environ["MCP_PORT"] = str(port)
        sys.argv = ["run_server.py", "--port", str(port)]
    sys.exit(run_http_web())
