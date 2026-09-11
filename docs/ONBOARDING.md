# Onboarding — database-operations-mcp

No wrappee install and no online account are required. SQLite works out of the box;
PostgreSQL/MySQL/MongoDB/Redis are optional external servers you connect to.

## Sanity check

```powershell
uv sync --extra dev
uv run database-operations-mcp --help
uv run pytest tests/unit/test_web_api.py -q
```

Then open the dashboard: `cd web_sota; .\start.ps1` → http://localhost:10708
(onboarding cue: `data-testid="onboarding-cue"` appears under the Dashboard hero).

Onboarding: N/A (no wrappee, no account) — this file is the rationale per ONBOARDING_STANDARD.
