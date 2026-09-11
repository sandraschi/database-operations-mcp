# Development — database-operations-mcp

```powershell
uv sync --extra dev        # install
just serve                 # backend 10709
just test                  # unit tests
just lint                  # ruff + biome
just ci                    # five-gate: ruff, format-check, pyright, pytest
```

Entry points: `src/database_operations_mcp/main.py` (stdio/HTTP/dual),
`src/database_operations_mcp/http_app.py` (FastAPI bridge),
`web_sota/` (Vite frontend 10708 → proxy /api → 10709).
