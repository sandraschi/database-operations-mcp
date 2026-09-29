import { useMutation } from "@tanstack/react-query";
import {
  ChevronRight,
  Database,
  FileJson,
  Play,
  Plus,
  RefreshCw,
  SearchCheck,
  Table,
  X,
} from "lucide-react";
import { useState } from "react";
import { callTool } from "@/common/api";
import { cn } from "@/common/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const ROW_LIMIT = 500;

type Row = Record<string, unknown>;
interface QueryTab {
  id: number;
  title: string;
  sql: string;
}

function extractData(res: unknown): Record<string, unknown> | null {
  if (res && typeof res === "object" && "data" in res)
    return (res as { data?: Record<string, unknown> }).data ?? null;
  if (res && typeof res === "object") return res as Record<string, unknown>;
  return null;
}

function itemName(item: unknown, keys: string[]): string {
  if (typeof item === "string") return item;
  if (item && typeof item === "object") {
    const obj = item as Record<string, unknown>;
    for (const k of keys) if (obj[k] != null) return String(obj[k]);
    return JSON.stringify(item);
  }
  return String(item);
}

function quoteIdent(name: string): string {
  return /^[A-Za-z_][A-Za-z0-9_]*$/.test(name)
    ? name
    : `"${name.replace(/"/g, '""')}"`;
}

function cellText(v: unknown): string {
  if (v == null) return "";
  return typeof v === "object" ? JSON.stringify(v) : String(v);
}

function toCsv(columns: string[], rows: Row[]): string {
  const esc = (v: unknown) => {
    const s = cellText(v);
    return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  return [
    columns.map(esc).join(","),
    ...rows.map((r) => columns.map((c) => esc(r[c])).join(",")),
  ].join("\n");
}

function download(filename: string, mime: string, content: string) {
  const url = URL.createObjectURL(new Blob([content], { type: mime }));
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export default function SQLExplorer() {
  const [connectionName, setConnectionName] = useState("");
  const [tables, setTables] = useState<string[] | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [columnsByTable, setColumnsByTable] = useState<
    Record<string, string[]>
  >({});
  const [tabs, setTabs] = useState<QueryTab[]>([
    { id: 1, title: "Query 1", sql: "SELECT 1" },
  ]);
  const [activeId, setActiveId] = useState(1);
  const [nextId, setNextId] = useState(2);
  const [columns, setColumns] = useState<string[]>([]);
  const [rows, setRows] = useState<Row[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const conn = connectionName.trim();
  const activeTab = tabs.find((t) => t.id === activeId) ?? tabs[0];

  const setActiveSql = (sql: string) =>
    setTabs((ts) => ts.map((t) => (t.id === activeTab.id ? { ...t, sql } : t)));

  const listTablesMutation = useMutation({
    mutationFn: (c: string) =>
      callTool("db_schema", { operation: "list_tables", connection_name: c }),
    onSuccess: (data) => {
      setError(null);
      const d = extractData(data?.result);
      const list = (d?.tables as unknown[]) ?? (d?.items as unknown[]) ?? [];
      setTables(
        (Array.isArray(list) ? list : []).map((i) =>
          itemName(i, ["table_name", "name", "full_name", "table"]),
        ),
      );
      setExpanded(null);
      setColumnsByTable({});
    },
    onError: (e: Error) => setError(e.message),
  });

  const describeMutation = useMutation({
    mutationFn: ({ c, table }: { c: string; table: string }) =>
      callTool("db_schema", {
        operation: "describe_table",
        connection_name: c,
        table_name: table,
      }),
    onSuccess: (data, { table }) => {
      const d = extractData(data?.result);
      const raw = d?.columns ?? d?.fields ?? [];
      const names = (Array.isArray(raw) ? raw : [])
        .map((col) => itemName(col, ["name", "column_name"]))
        .filter(Boolean);
      setColumnsByTable((m) => ({ ...m, [table]: names }));
    },
    onError: (e: Error) => setError(e.message),
  });

  const runMutation = useMutation({
    mutationFn: ({ c, sql }: { c: string; sql: string }) =>
      callTool("db_operations", {
        operation: "execute_query",
        connection_name: c,
        query: sql,
        limit: ROW_LIMIT,
      }),
    onSuccess: (data) => {
      setError(null);
      const d = extractData(data?.result);
      const rawRows = d?.rows ?? d?.result ?? [];
      const declared = Array.isArray(d?.columns)
        ? (d.columns as unknown[]).map((c) => String(c))
        : [];
      const list = Array.isArray(rawRows) ? rawRows : [];
      // Rows may be dicts or positional arrays depending on the connector.
      const normalized: Row[] = list.map((r) =>
        Array.isArray(r)
          ? Object.fromEntries(
              r.map((v, i) => [declared[i] ?? `col${i + 1}`, v]),
            )
          : ((r ?? {}) as Row),
      );
      setColumns(
        declared.length > 0
          ? declared
          : normalized.length > 0
            ? Object.keys(normalized[0])
            : [],
      );
      setRows(normalized);
    },
    onError: (e: Error) => {
      setError(e.message);
      setRows(null);
    },
  });

  const loadSchema = () => {
    if (!conn) {
      setError("Enter a connection name.");
      return;
    }
    listTablesMutation.mutate(conn);
  };

  const onTableClick = (table: string) => {
    setActiveSql(`SELECT * FROM ${quoteIdent(table)} LIMIT 100;`);
    if (expanded === table) {
      setExpanded(null);
      return;
    }
    setExpanded(table);
    if (!columnsByTable[table]) describeMutation.mutate({ c: conn, table });
  };

  const runQuery = () => {
    if (!conn) {
      setError("Enter a connection name.");
      return;
    }
    if (!activeTab.sql.trim()) {
      setError("Enter a query.");
      return;
    }
    runMutation.mutate({ c: conn, sql: activeTab.sql.trim() });
  };

  const addTab = () => {
    setTabs((ts) => [...ts, { id: nextId, title: `Query ${nextId}`, sql: "" }]);
    setActiveId(nextId);
    setNextId(nextId + 1);
  };

  const closeTab = (id: number) => {
    if (tabs.length === 1) return;
    const remaining = tabs.filter((t) => t.id !== id);
    setTabs(remaining);
    if (activeId === id) setActiveId(remaining[0].id);
  };

  return (
    <div className="grid grid-cols-12 gap-6" data-testid="sql-explorer-page">
      <div className="col-span-3 space-y-4">
        <Card
          className="border-slate-800 bg-slate-950/50"
          data-testid="sql-explorer-schema-browser"
        >
          <CardHeader className="p-4 space-y-3">
            <CardTitle className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Schema Browser
            </CardTitle>
            <input
              className="h-8 w-full rounded-md border border-slate-800 bg-slate-900 px-2 text-xs text-slate-100 placeholder:text-slate-500"
              value={connectionName}
              onChange={(e) => setConnectionName(e.target.value)}
              placeholder="Connection name"
              data-testid="sql-explorer-connection-input"
            />
            <Button
              size="sm"
              variant="secondary"
              onClick={loadSchema}
              disabled={!conn || listTablesMutation.isPending}
              data-testid="sql-explorer-load-schema-button"
            >
              <RefreshCw
                className={cn(
                  "h-3 w-3 mr-2",
                  listTablesMutation.isPending && "animate-spin",
                )}
              />
              {tables === null ? "Load schema" : "Reload"}
            </Button>
          </CardHeader>
          <CardContent className="p-0" data-testid="sql-explorer-tree">
            {tables === null && (
              <p className="px-4 pb-4 text-xs text-slate-500">
                Enter a connection name and load its tables.
              </p>
            )}
            {tables !== null && (
              <>
                <div className="flex items-center gap-2 px-4 py-2 text-slate-200">
                  <Database className="h-3.5 w-3.5 text-blue-500" />
                  <span className="text-sm font-medium truncate">{conn}</span>
                </div>
                {tables.length === 0 && (
                  <p className="px-4 pb-4 text-xs text-slate-500">
                    No tables found.
                  </p>
                )}
                <div className="ml-6 border-l border-slate-800 pb-2">
                  {tables.map((t) => (
                    <div key={t}>
                      <button
                        type="button"
                        onClick={() => onTableClick(t)}
                        className="flex w-full items-center gap-2 px-3 py-1.5 text-left text-xs text-slate-400 hover:text-white transition-colors"
                        data-testid={`sql-explorer-table-${t}`}
                      >
                        <ChevronRight
                          className={cn(
                            "h-3 w-3 transition-transform",
                            expanded === t && "rotate-90",
                          )}
                        />
                        <Table className="h-3 w-3" />
                        <span className="truncate">{t}</span>
                      </button>
                      {expanded === t && (
                        <div className="ml-9 pb-1 text-[11px] text-slate-500 font-mono">
                          {columnsByTable[t] ? (
                            columnsByTable[t].map((c) => (
                              <div key={c} className="truncate">
                                {c}
                              </div>
                            ))
                          ) : (
                            <div>loading...</div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="col-span-9 space-y-6">
        {error && (
          <div
            className="rounded-md border border-red-900/50 bg-red-950/20 px-4 py-2 text-sm text-red-400"
            data-testid="sql-explorer-error"
          >
            {error}
          </div>
        )}

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between py-2 border-b border-slate-800">
            <div className="flex items-center gap-1">
              {tabs.map((t) => (
                <div
                  key={t.id}
                  className={cn(
                    "flex items-center gap-1 rounded px-2 py-1 text-xs",
                    t.id === activeTab.id
                      ? "bg-slate-800 text-white"
                      : "text-slate-400 hover:text-white",
                  )}
                >
                  <button
                    type="button"
                    onClick={() => setActiveId(t.id)}
                    data-testid={`sql-explorer-tab-${t.id}`}
                  >
                    {t.title}
                  </button>
                  {tabs.length > 1 && (
                    <button
                      type="button"
                      onClick={() => closeTab(t.id)}
                      aria-label={`Close ${t.title}`}
                    >
                      <X className="h-3 w-3" />
                    </button>
                  )}
                </div>
              ))}
              <Button
                size="sm"
                variant="ghost"
                className="h-6 w-6 p-0 text-slate-400"
                onClick={addTab}
                aria-label="New query tab"
                data-testid="sql-explorer-add-tab-button"
              >
                <Plus className="h-3 w-3" />
              </Button>
            </div>
            <Button
              size="sm"
              className="bg-emerald-600 hover:bg-emerald-700 text-white"
              onClick={runQuery}
              disabled={runMutation.isPending || !conn || !activeTab.sql.trim()}
              data-testid="sql-explorer-run-button"
            >
              <Play className="h-3 w-3 mr-2" />
              {runMutation.isPending ? "Running..." : "Run Query"}
            </Button>
          </CardHeader>
          <CardContent className="p-4">
            <textarea
              className="font-mono text-sm min-h-[150px] w-full bg-black/30 rounded p-4 text-emerald-400/80 placeholder:text-slate-600"
              value={activeTab.sql}
              onChange={(e) => setActiveSql(e.target.value)}
              onKeyDown={(e) => {
                if ((e.ctrlKey || e.metaKey) && e.key === "Enter") runQuery();
              }}
              placeholder="SELECT * FROM ...  (Ctrl+Enter to run)"
              spellCheck={false}
              data-testid="sql-explorer-query-input"
            />
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="py-2 border-b border-slate-800 flex flex-row items-center justify-between">
            <CardTitle className="text-xs font-bold uppercase text-slate-400">
              Results{rows ? ` (${rows.length} rows)` : ""}
            </CardTitle>
            <div className="flex gap-2">
              <Button
                size="sm"
                variant="ghost"
                className="h-6 text-[10px] gap-1"
                disabled={!rows || rows.length === 0}
                onClick={() =>
                  rows &&
                  download(
                    "results.json",
                    "application/json",
                    JSON.stringify(rows, null, 2),
                  )
                }
                data-testid="sql-explorer-export-json-button"
              >
                <FileJson className="h-3 w-3" /> JSON
              </Button>
              <Button
                size="sm"
                variant="ghost"
                className="h-6 text-[10px] gap-1"
                disabled={!rows || rows.length === 0}
                onClick={() =>
                  rows &&
                  download("results.csv", "text/csv", toCsv(columns, rows))
                }
                data-testid="sql-explorer-export-csv-button"
              >
                <SearchCheck className="h-3 w-3" /> CSV
              </Button>
            </div>
          </CardHeader>
          <CardContent className="p-0" data-testid="sql-explorer-results">
            {rows === null ? (
              <p className="p-4 text-xs text-slate-500">
                Run a query to see results.
              </p>
            ) : rows.length === 0 ? (
              <p className="p-4 text-xs text-slate-500">
                Query returned no rows.
              </p>
            ) : (
              <div className="max-h-[400px] overflow-auto">
                <table className="w-full text-xs text-left">
                  <thead className="sticky top-0 bg-slate-900 text-slate-500 uppercase tracking-wider font-bold">
                    <tr>
                      {columns.map((c) => (
                        <th
                          key={c}
                          className="px-4 py-2 border-b border-slate-800"
                        >
                          {c}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="text-slate-300">
                    {rows.map((row, i) => (
                      <tr key={i} className="hover:bg-slate-800/30">
                        {columns.map((c) => (
                          <td
                            key={c}
                            className="px-4 py-2 border-b border-slate-900 font-mono"
                          >
                            {cellText(row[c])}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
