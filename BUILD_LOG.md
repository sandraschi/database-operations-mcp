# BUILD_LOG.md - database-operations-mcp

Running record for packaging builds (MCPB + Tauri NSIS).
Required by the NSIS build gate: document failures, regressions, fixes.

## 2026-09-12 - v1.4.1 MCPB + NSIS (setup.exe + .mcpb)

### Artifacts (in `dist/`, gitignored, not committed)
- `dist/database-operations-mcp-v1.4.1.mcpb` - 227 KB, 87 files
- `dist/Database Operations MCP_0.1.0_x64-setup.exe` - 108.9 MB (NSIS, currentUser)
- `dist/database-operations-mcp-backend.exe` - 107 MB (PyInstaller onefile sidecar)

### Gates (all green unless noted)
- `ruff check src/ tests/` - pass
- `ruff format --check src/ tests/` - pass
- `pytest tests/unit/ -q` - pass (8 pre-existing skips: stdio/subprocess + strict meta tests)
- `tsc --noEmit` (web_sota) - pass
- `biome ci` (web_sota) - warnings only, exit 0 (see residuals)
- Sidecar smoke: `PORT=10709` + TAURI env, `/health` 200, `/api/v1/diagnostics` 200
- Chat routes: `GET /api/v1/settings/llm` 200 (ollama/gemma4:e4b),
  `POST /api/v1/chat` 200 with clean no-backend dialogic reply
- MCPB 3-4-100: system=3515, user=4501, examples=101 - PASS
- MCPB import check: `database_operations_mcp.http_app` resolves from `mcpb/src` only - PASS
- MCPB pollution check: zero `*.bak` / `*.pyc` in bundle - PASS (after fix #2)

### Failures encountered and fixes
1. Manual `Copy-Item src/database_operations_mcp mcpb/src/database_operations_mcp`
   created `mcpb/src/database_operations_mcp/database_operations_mcp` (double nest,
   broken import). Fixed by copying to `mcpb/src/` so the package dir lands once.
   Lesson: follow the fresh-stage fragment exactly (copy package INTO `mcpb/src/`).
2. First `.mcpb` (104 files) shipped 10 `*.bak` twins copied from `src/`.
   Fixed by deleting 17 `*.bak` files under `src/` (gitignored sidecars, content
   already committed) + ensuring `mcpb/.mcpbignore` exists at pack root before pack.
   Rebuilt clean: 87 files, `ignored files: 1`.
3. `make-mcpb.ps1` regenerates `mcpb/manifest.json` etc. on every run (tool list
   refresh: +chat_interaction, +refine_prompt, +api_diagnostics, ...). Expected
   churn - committed as `chore(mcpb)`.
4. `Start-Process dist/...-backend.exe` failed once with `spawn EPERM` - cause was
   a stale backend process from the earlier smoke test holding state.
   Fixed by killing leftovers first (Phase 0 precondition). No code change.
5. `npx playwright test` fails: `@playwright/test` not in `web_sota/package.json`
   (runner missing) + `playwright.config.ts` webServer points at nonexistent
   `database_operations_mcp.server` module on port 10708. Pre-existing broken
   e2e track, unrelated to this build. Left as residual (see below), verified
   via sidecar smoke + route checks instead.

### Source changes shipped with this build
- `src/.../tools/agentic_tools.py`: removed `safety_override` bypass,
  always-on `ENFORCED` guard, `confirm` + `dry_run` (default True),
  `max_steps` clamped 1-10.
- `native/src/main.rs`: handle `ExitRequested` like `Exit` (kill + wait child).
- `native/src/backend.rs`: removed `mut` on spawned child (tauri build warning).
- `assets/prompts/*`: live 3-4-100 copies synced from `mcpb/assets/prompts`.
- `mcpb/.mcpbignore`: pack-root ignore so `.bak` never ships again.

### Residuals / known gaps (not blocking this build)
- `biome ci`: 6 warnings + 3 infos (e2e template concat, settings concat,
  vite `node:` protocol, `any` in apps-catalog/db-browser, `!` in main.tsx,
  comma operator in chat.tsx, unused `e` in db-browser catch). Pre-existing.
- `@tauri-apps/api` not in frontend deps: no `backend-status` event bridge;
  chat polls via fetch, works without it. Add when wiring instant refresh.
- Tauri `csp: null` (no CSP enforcement). Fine for localhost backend, tighten later.
- Playwright e2e track broken (missing runner dep + stale webServer command).
  Repair = add `@playwright/test`, fix webServer to real backend + vite FE.
- `native/resources/*.exe` (112 MB) and `.agents/` / `.opencode/` stay untracked.
