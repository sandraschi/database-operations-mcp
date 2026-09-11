# Configuration — database-operations-mcp

| Var | Default | Purpose |
|-----|---------|---------|
| MCP_TRANSPORT | dual | stdio \| http \| dual |
| MCP_HOST | 127.0.0.1 | HTTP bind host |
| MCP_PORT | 10709 | Backend port (fleet registry; frontend 10708) |
| CORS_ORIGINS | localhost:10708/10709 + tauri://localhost | Comma-separated allow-list (never `*`) |
| LOG_LEVEL | INFO | Logging verbosity |
| ENABLE_PASSWORD_STORAGE | 0 | Dev-only connection password persistence |
| ENABLE_ATOMIC_DB_TOOLS | true | Register db_atomic opt-in tools |

See [.env.example](../.env.example). Ports: backend 10709, frontend 10708 (adjacent pair).
