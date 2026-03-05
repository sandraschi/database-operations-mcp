# Vector DB Support — Implementation Plan

**Status:** Planned (not yet implemented)  
**Date:** 2026-02-28  
**Priority:** Medium — driven by active RAG usage in speech-mcp and advanced-memory-mcp  
**Supersedes:** LANCEDB_CONNECTOR_PLAN.md (archived, scope expanded)

---

## Background

Vector/RAG databases are now first-class citizens in the fleet:

- `speech-mcp` — knowledge base RAG (FastEmbed + LanceDB)
- `advanced-memory-mcp` — semantic note retrieval (LanceDB)
- Future projects — any RAG pipeline will likely use LanceDB or ChromaDB

`database-operations-mcp` (dbops) currently supports: SQLite, PostgreSQL, MySQL, Redis, DuckDB, MongoDB, ChromaDB.

**Gaps:**
- LanceDB connector is entirely missing
- ChromaDB connector exists but lacks vector-aware operations (no `vector_search`, no `hybrid_search`, no index/distance metric info)
- The webapp UI has no vector-specific pages — vector stores are treated like generic tables, losing all meaningful context

---

## Scope

1. New `lancedb_connector.py`
2. Upgrade `chromadb_connector.py` with vector-aware methods
3. New `db_vector` portmanteau MCP tool (shared interface for both backends)
4. New webapp pages: Vector Explorer, Similarity Search, Collection Inspector

---

## 1. LanceDB Connector

**File:** `src/database_operations_mcp/connectors/lancedb_connector.py`

| Method | Description |
|---|---|
| `connect(uri)` | Open local path or LanceDB Cloud URI |
| `health_check()` | Verify connection, return table count |
| `list_tables()` | Return all table names |
| `describe_table(name)` | Schema: columns, vector dim, row count, distance metric |
| `query(table, filter, limit)` | Metadata/SQL-style filter query |
| `vector_search(table, embedding, limit, filter)` | ANN similarity search |
| `insert(table, records)` | Add records (with pre-computed embeddings) |
| `create_table(name, schema)` | Create new table with schema |
| `delete_table(name)` | Drop a table |

**Dependency:** `lancedb>=0.6.0` → add to `pyproject.toml`

**Connection config:**
```python
db_connection(
    operation="register",
    connection_name="speech_rag",
    database_type="lancedb",
    connection_config={"uri": "C:/Users/sandr/AppData/Local/speech-mcp/lancedb"}
)
```

---

## 2. ChromaDB Connector Upgrade

ChromaDB connector exists but needs vector-aware methods added:

| Method | Status | Action |
|---|---|---|
| `connect()` | ✅ exists | keep |
| `list_tables()` | ✅ exists | keep |
| `describe_table(name)` | ⚠️ partial | add embedding dim, distance metric, hnsw params |
| `vector_search(collection, embedding, limit, filter)` | ❌ missing | add |
| `hybrid_search(collection, embedding, filter, limit)` | ❌ missing | add |
| `list_indexes(collection)` | ❌ missing | add |
| `get_distance_metric(collection)` | ❌ missing | add |

---

## 3. `db_vector` Portmanteau Tool

New MCP tool with a unified interface across LanceDB and ChromaDB (and future vector backends).

**Operations:**

| Operation | Description | Required params |
|---|---|---|
| `vector_search` | ANN similarity search with pre-computed embedding | connection_name, table_name, embedding (list[float]), limit |
| `hybrid_search` | Vector + metadata filter combined | connection_name, table_name, embedding, filter (dict), limit |
| `list_indexes` | Show vector indexes on a collection/table | connection_name, table_name |
| `describe_collection` | Full collection info: dims, metric, row count, index params | connection_name, table_name |
| `reindex` | Rebuild vector index | connection_name, table_name |
| `list_collections` | All collections/tables with basic stats | connection_name |

Note: embedding generation (text → vector) stays out of scope for dbops. Callers pass pre-computed embeddings. For interactive webapp use, the UI can optionally call an embedding endpoint.

---

## 4. Webapp — Vector DB Pages

This is a separate but equally important deliverable. The existing webapp treats vector stores like generic SQL tables, which is useless for RAG debugging.

### 4a. Vector Explorer Page (`/vector`)

Landing page for all vector connections.

- List registered vector connections (LanceDB, ChromaDB)
- Per-connection: collection count, total vectors, embedding model (if stored), distance metric
- Quick "connect" form for new LanceDB/ChromaDB URIs
- Link through to Collection Inspector per connection

### 4b. Collection Inspector Page (`/vector/:connection/:collection`)

Deep dive into a single collection/table.

- Schema table: column names, types, vector dimension
- Index info: distance metric (cosine/L2/IP), HNSW params if available
- Row count, estimated storage size
- Sample rows with vector preview (first N dims shown, full shown on expand)
- Metadata filter builder — construct filter queries visually, run against collection
- Export sample to JSON/CSV

### 4c. Similarity Search Page (`/vector/:connection/:collection/search`)

Interactive RAG debugging tool.

- Input: raw text query OR paste raw embedding (JSON array)
- If text: optional embedding endpoint field (user provides their embedder URL, dbops calls it)
- Sliders: top-K results, distance threshold
- Optional metadata filter panel
- Results table: rank, distance score, all metadata columns, vector preview
- Side-by-side diff view for comparing two queries
- "Why did this chunk rank here?" — show distance score prominently

### 4d. Hybrid Search Tab (within Similarity Search)

- Add metadata filter panel alongside vector query
- Show which results were filtered vs ranked out

### 4e. Sidebar / Nav Updates

- Add "Vector DBs" section to the main nav
- Separate from "SQL Databases" and "NoSQL"
- Icon: something embedding-y — lattice or node graph

---

## Estimated Effort

| Task | Time |
|---|---|
| `lancedb_connector.py` | ~2h |
| ChromaDB connector upgrade | ~2h |
| Wire both into `db_connection`, `db_schema`, `db_operations` | ~1h |
| `db_vector` portmanteau tool | ~3h |
| Webapp: Vector Explorer page | ~2h |
| Webapp: Collection Inspector page | ~3h |
| Webapp: Similarity Search page | ~4h |
| Tests + docs | ~1h |
| **Total** | **~2 days** |

---

## Notes

- LanceDB and ChromaDB have compatible enough APIs that the `db_vector` abstraction layer is straightforward.
- The webapp similarity search page is arguably the most valuable single deliverable — it turns RAG debugging from "write ad-hoc Python" into a point-and-click workflow.
- LanceDB Cloud (remote URI) support optional; local file-based is primary.
- ChromaDB remote (HTTP client mode) already partially supported — confirm during upgrade.
