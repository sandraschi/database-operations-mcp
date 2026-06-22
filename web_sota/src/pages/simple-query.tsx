import { useMutation } from "@tanstack/react-query";
import { Loader2, Play } from "lucide-react";
import { useState } from "react";
import { callTool } from "@/common/api";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";

function extractData(res: unknown): Record<string, unknown> | null {
  if (res && typeof res === "object" && "data" in res)
    return (res as { data?: Record<string, unknown> }).data ?? null;
  if (res && typeof res === "object") return res as Record<string, unknown>;
  return null;
}

export function SimpleQuery() {
  const [connectionName, setConnectionName] = useState("");
  const [tables, setTables] = useState<string[]>([]);
  const [selectedTable, setSelectedTable] = useState("");
  const [columns, setColumns] = useState<string[]>([]);
  const [selectedColumns, setSelectedColumns] = useState<string[]>([]);
  const [limit, setLimit] = useState(100);
  const [filterCol, setFilterCol] = useState("");
  const [filterOp, setFilterOp] = useState("=");
  const [filterVal, setFilterVal] = useState("");
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [error, setError] = useState<string | null>(null);

  const listTablesMutation = useMutation({
    mutationFn: (conn: string) =>
      callTool("db_schema", {
        operation: "list_tables",
        connection_name: conn,
      }),
    onSuccess: (data) => {
      setError(null);
      const d = extractData(data?.result);
      const list = (d?.tables as unknown[]) ?? (d?.items as unknown[]) ?? [];
      const tableNames = list.map((item: unknown) => {
        if (typeof item === "string") return item;
        if (item && typeof item === "object") {
          const obj = item as Record<string, unknown>;
          return String(
            obj.table_name ??
              obj.name ??
              obj.full_name ??
              obj.table ??
              JSON.stringify(item),
          );
        }
        return String(item);
      });
      setTables(Array.isArray(tableNames) ? tableNames : []);
      setSelectedTable("");
      setColumns([]);
      setSelectedColumns([]);
    },
    onError: (e: Error) => setError(e.message),
  });

  const describeMutation = useMutation({
    mutationFn: ({ conn, table }: { conn: string; table: string }) =>
      callTool("db_schema", {
        operation: "describe_table",
        connection_name: conn,
        table_name: table,
      }),
    onSuccess: (data) => {
      setError(null);
      const d = extractData(data?.result);
      const rawCols = d?.columns ?? d?.fields ?? [];
      const cols = Array.isArray(rawCols) ? rawCols : [];
      const names = cols
        .map((c: unknown) =>
          typeof c === "string" ? c : ((c as { name?: string }).name ?? ""),
        )
        .filter(Boolean) as string[];
      if (names.length === 0 && d?.schema) {
        const schema = d.schema as Record<string, unknown>;
        setColumns(Object.keys(schema));
      } else {
        setColumns(names);
      }
      setSelectedColumns(names);
    },
    onError: (e: Error) => setError(e.message),
  });

  const runMutation = useMutation({
    mutationFn: ({ conn, query }: { conn: string; query: string }) =>
      callTool("db_operations", {
        operation: "execute_query",
        connection_name: conn,
        query,
        limit: limit + 1,
      }),
    onSuccess: (data) => {
      setError(null);
      const d = extractData(data?.result);
      const list =
        (d?.rows as Record<string, unknown>[]) ??
        (d?.result as Record<string, unknown>[]) ??
        [];
      setRows(Array.isArray(list) ? list : []);
    },
    onError: (e: Error) => setError(e.message),
  });

  const loadTables = () => {
    if (!connectionName.trim()) {
      setError("Enter connection name.");
      return;
    }
    listTablesMutation.mutate(connectionName.trim());
  };

  const onSelectTable = (table: string) => {
    setSelectedTable(table);
    if (!connectionName.trim()) return;
    describeMutation.mutate({ conn: connectionName.trim(), table });
    setFilterCol("");
    setFilterVal("");
  };

  const toggleColumn = (col: string) => {
    setSelectedColumns((prev) =>
      prev.includes(col) ? prev.filter((c) => c !== col) : [...prev, col],
    );
  };

  const runQuery = () => {
    if (!connectionName.trim() || !selectedTable) {
      setError("Select a connection and table.");
      return;
    }
    const cols =
      selectedColumns.length > 0
        ? selectedColumns.map((c) => `"${c}"`).join(", ")
        : "*";
    let query = `SELECT ${cols} FROM "${selectedTable}"`;
    if (filterCol && filterVal.trim() !== "") {
      const op = filterOp === "LIKE" ? " LIKE " : ` ${filterOp} `;
      const val =
        filterOp === "LIKE"
          ? `'%${filterVal.replace(/'/g, "''")}%'`
          : `'${String(filterVal).replace(/'/g, "''")}'`;
      query += ` WHERE "${filterCol}"${op}${val}`;
    }
    query += ` LIMIT ${Math.min(limit, 1000)}`;
    runMutation.mutate({ conn: connectionName.trim(), query });
  };

  const displayCols =
    columns.length > 0
      ? columns
      : rows.length > 0
        ? Object.keys(rows[0] as object)
        : [];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">
          Simple query
        </h2>
        <p className="text-slate-400">
          Pick a table and columns, add an optional filter — no SQL needed
        </p>
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white">Connection and table</CardTitle>
          <CardDescription className="text-slate-400">
            Load tables, then pick one to choose columns.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap items-end gap-4">
          <div className="grid gap-2">
            <Label className="text-slate-300">Connection name</Label>
            <input
              className="h-9 w-52 rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100 placeholder:text-slate-500"
              value={connectionName}
              onChange={(e) => setConnectionName(e.target.value)}
              placeholder="e.g. local_sqlite"
            />
          </div>
          <Button
            className="bg-blue-600 hover:bg-blue-700"
            onClick={loadTables}
            disabled={listTablesMutation.isPending || !connectionName.trim()}
          >
            {listTablesMutation.isPending ? "Loading..." : "Load tables"}
          </Button>
          {tables.length > 0 && (
            <>
              <div className="grid gap-2">
                <Label className="text-slate-300">Table</Label>
                <select
                  className="h-9 min-w-[160px] rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100"
                  value={selectedTable}
                  onChange={(e) => onSelectTable(e.target.value)}
                >
                  <option value="">Select table</option>
                  {tables.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              </div>
              {columns.length > 0 && (
                <div className="grid gap-2">
                  <Label className="text-slate-300">
                    Columns (click to toggle)
                  </Label>
                  <div className="flex flex-wrap gap-2">
                    {columns.map((c) => (
                      <button
                        key={c}
                        type="button"
                        onClick={() => toggleColumn(c)}
                        className={`rounded px-2 py-1 text-xs font-mono ${
                          selectedColumns.includes(c)
                            ? "bg-blue-600 text-white"
                            : "bg-slate-800 text-slate-400 hover:bg-slate-700"
                        }`}
                      >
                        {c}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {selectedTable && columns.length > 0 && (
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white">Filter and limit</CardTitle>
            <CardDescription className="text-slate-400">
              Optional: one filter and max rows.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap items-end gap-4">
            <div className="grid gap-2">
              <Label className="text-slate-300">Where column</Label>
              <select
                className="h-9 min-w-[120px] rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100"
                value={filterCol}
                onChange={(e) => setFilterCol(e.target.value)}
              >
                <option value="">—</option>
                {columns.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>
            <div className="grid gap-2">
              <Label className="text-slate-300">Operator</Label>
              <select
                className="h-9 w-24 rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100"
                value={filterOp}
                onChange={(e) => setFilterOp(e.target.value)}
              >
                <option value="=">=</option>
                <option value="!=">!=</option>
                <option value=">">&gt;</option>
                <option value="<">&lt;</option>
                <option value="LIKE">LIKE</option>
              </select>
            </div>
            <div className="grid gap-2">
              <Label className="text-slate-300">Value</Label>
              <input
                className="h-9 w-40 rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100 placeholder:text-slate-500"
                value={filterVal}
                onChange={(e) => setFilterVal(e.target.value)}
                placeholder="Leave empty for no filter"
              />
            </div>
            <div className="grid gap-2">
              <Label className="text-slate-300">Limit</Label>
              <input
                type="number"
                min={1}
                max={1000}
                className="h-9 w-20 rounded-md border border-slate-800 bg-slate-900 px-2 text-sm text-slate-100"
                value={limit}
                onChange={(e) => setLimit(Number(e.target.value) || 100)}
              />
            </div>
            <Button
              className="bg-emerald-600 hover:bg-emerald-700"
              onClick={runQuery}
              disabled={runMutation.isPending}
            >
              {runMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Play className="mr-2 h-4 w-4" />
              )}
              Run query
            </Button>
          </CardContent>
        </Card>
      )}

      {error && (
        <div className="rounded-md border border-red-900/50 bg-red-950/20 px-4 py-2 text-sm text-red-400">
          {error}
        </div>
      )}

      {rows.length > 0 && (
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white">
              Result ({rows.length} rows)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="w-full rounded border border-slate-800">
              <div className="min-w-0 overflow-x-auto">
                <table className="w-full border-collapse text-sm">
                  <thead>
                    <tr className="border-b border-slate-700 bg-slate-900/50">
                      {displayCols.map((col) => (
                        <th
                          key={col}
                          className="text-left px-4 py-2 font-medium text-slate-300 whitespace-nowrap"
                        >
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((row, i) => (
                      <tr
                        key={i}
                        className="border-b border-slate-800 hover:bg-slate-800/30"
                      >
                        {displayCols.map((col) => (
                          <td
                            key={col}
                            className="px-4 py-2 text-slate-300 whitespace-nowrap max-w-[200px] truncate"
                          >
                            {String(
                              (row as Record<string, unknown>)[col] ?? "",
                            )}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
