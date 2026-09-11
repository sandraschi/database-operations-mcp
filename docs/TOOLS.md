# Tools — database-operations-mcp

Portmanteau tools (each takes `operation=`):

| Tool | Operations |
|------|------------|
| db_connection | list_supported, register, init, list, test, test_all, close, get_info, restore, set_active, get_active, get_preferences, set_preferences |
| db_operations | execute_query, execute_transaction, execute_write, batch_insert, quick_data_sample, export_query_results |
| db_schema | list_databases, list_tables, describe_table, get_schema_diff |
| db_management | health, metrics, vacuum, backup/restore helpers |
| db_fts | search, list_tables, suggest |
| db_analyzer | analyze, diagnostics |
| media_library | Calibre + Plex library ops |
| windows_system | registry, services, system info |
| help_system | help, examples, search |
| system_init | setup |
| agentic_workflow_tool | sampling orchestration (SEP-2577 deprecated path; migrate to direct LLM calls) |

Every tool returns `{success, message, ...}` (dialogic shape). REST: `/api/tools`, `/api/tools/call`, `/api/capabilities`, `/api/health`.
