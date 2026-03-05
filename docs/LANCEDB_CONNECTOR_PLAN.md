# LanceDB Connector — Implementation Plan

**Status:** SUPERSEDED — see VECTOR_DB_PLAN.md  
**Status:** Planned (not yet implemented)  
**Date:** 2026-02-28  
**Priority:** Medium — driven by active RAG usage in speech-mcp and advanced-memory-mcp

---

## Background

LanceDB is now actively used in the fleet for vector/RAG storage:

- `speech-mcp` — knowledge base RAG (FastEmbed + LanceDB)
- `advanced-memory-mcp` — semantic note retrieval

The `database-operations-mcp` (dbops) currently supports: SQLite, PostgreSQL, MySQL, Redis, DuckDB, MongoDB, ChromaDB.  
**LanceDB is missing**, leaving a gap: there is no way to inspect, query, or manage LanceDB stores through dbops tooling.

---

## What Needs to Be Built

### 1. `lancedb_connector.py`

New file: `src/database_operations_mcp/connectors/lancedb_connector.py`

Core methods to implement:

| Method | Description |
|---|---|
| `connect(uri)` | Open local path or LanceDB Cloud URI |
| `health_check()` | Verify connection, return table count |
| `list_tables()` | Return all table names |
| `describe_table(name)` | Schema: columns, vector dim, row count |
| `query(table, filter, limit)` | Metadata/SQL-style filter query |
| `vector_search(table, embedding, limit, filter)` | ANN similarity search |
| `insert(table, records)` | Add records (with or without pre-computed embeddings) |
| `create_table(name, schema)` | Create new table with schema |
| `delete_table(name)` | Drop a table |

Dependencies to add to `pyproject.toml`:
```
lancedb>=0.6.0
```

### 2. Wire into existing portmanteau tools

| Tool | Changes needed |
|---|---|
| `db_connection` | Add `lancedb` as valid `database_type`; `connection_config` = `{"uri": "/path/to/db"}` |
| `db_schema` | `list_tables`, `describe_table` via LanceDB connector |
| `db_operations` | `execute_query` (filter), `batch_insert`, `quick_data_sample` |
| `db_connection` → `list_supported` | Add LanceDB to the supported DB list |

### 3. New `db_vector` tool (or extend `db_fts`)

Option A — extend `db_fts` with new operations:
- `vector_search` — ANN search given a pre-computed embedding
- `hybrid_search` — combined vector + metadata filter

Option B — new `db_vector` portmanteau tool (preferred for clarity):

```
Operations:
- vector_search   : ANN similarity search (requires: table_name, embedding or query_text)
- hybrid_search   : vector + metadata filter combined
- list_indexes    : show vector indexes on a table
- reindex         : rebuild vector index
```

**Recommendation: Option B** — keeps vector ops clearly separated from FTS (which is text-only).

---

## Connection Config Example

```python
# Register a LanceDB connection
db_connection(
    operation="register",
    connection_name="speech_rag",
    database_type="lancedb",
    connection_config={"uri": "C:/Users/sandr/AppData/Local/speech-mcp/lancedb"}
)
```

---

## RAG-Specific Use Cases

Once implemented, dbops will be able to:

- Inspect which tables/collections exist in speech-mcp's knowledge base
- Run similarity searches directly via MCP tooling
- Batch-insert new documentation chunks
- Check row counts and schema to debug RAG quality issues
- Export LanceDB content to CSV/JSON for analysis

---

## Estimated Effort

| Task | Time |
|---|---|
| `lancedb_connector.py` | ~2h |
| Wire into `db_connection`, `db_schema`, `db_operations` | ~1h |
| `db_vector` tool (new portmanteau) | ~3h |
| Tests + docs update | ~1h |
| **Total** | **~1 day** |

---

## Notes

- LanceDB has a clean Python API (`lancedb.connect()`, `db.open_table()`, `.search()`) — connector will be straightforward.
- Embedding generation (text → vector) is **out of scope** for dbops; callers pass pre-computed embeddings or raw text for servers that embed internally.
- ChromaDB connector already exists and can serve as a reference pattern.
- LanceDB Cloud (remote URI) support should be optional — local file-based is the primary use case.
