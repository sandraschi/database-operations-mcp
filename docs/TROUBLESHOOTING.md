# Troubleshooting — database-operations-mcp

- Backend not reachable on 10709: `start.ps1` clears stale port owners and polls TCP 30s.
  Check `GET /api/health` → `{"status":"ok"}`.
- Frontend 10708 shows Offline: verify backend first, then `cd web_sota; npm run dev`.
- Tests: `uv run pytest tests/ -q`. Known failure tracked: `test_import_only.py::TestToolRegistration::test_tool_registration_count`.
- Pyright bulk (278 errors, mostly possibly-unbound `conn`/`backup_path`): fix incrementally per file; do not blanket-ignore.
- Logs: `/logs` page + `GET /api/logs`, `/api/logs/stats`, `/api/logs/export`.
