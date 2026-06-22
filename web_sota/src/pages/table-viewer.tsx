import { useMutation } from "@tanstack/react-query";
import { Loader2, Table2 } from "lucide-react";
import { useState } from "react";
import { callTool } from "@/common/api";
import { cn } from "@/common/utils";
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

export function TableViewer() {
  const [connectionName, setConnectionName] = useState("");
  const [tables, setTables] = useState<string[]>([]);
  const [selectedTable, setSelectedTable] = useState<string | null>(null);
  const [pageSize, setPageSize] = useState(25);
  const [page, setPage] = useState(1);
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [columns, setColumns] = useState<string[]>([]);
  const [rowCount, setRowCount] = useState<number | null>(null);
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
      setSelectedTable(null);
      setRows([]);
      setColumns([]);
    },
    onError: (e: Error) => setError(e.message),
  });

  const loadDataMutation = useMutation({
    mutationFn: ({
      conn,
      table,
      lim,
      offs,
    }: {
      conn: string;
      table: string;
      lim: number;
      offs: number;
    }) =>
      callTool("db_operations", {
        operation: "quick_data_sample",
        connection_name: conn,
        table_name: table,
        limit: lim,
        offset: offs,
      }),
    onSuccess: (data) => {
      setError(null);
      const d = extractData(data?.result);
      const sample =
        (d?.sample_data as Record<string, unknown>[]) ??
        (d?.rows as Record<string, unknown>[]) ??
        [];
      const cols =
        (d?.columns as string[]) ??
        (sample.length > 0 ? Object.keys(sample[0] as object) : []);
      setRows(Array.isArray(sample) ? sample : []);
      setColumns(Array.isArray(cols) ? cols : []);
      setRowCount(
        (d?.total_row_count as number) ??
          (d?.row_count as number) ??
          sample.length,
      );
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

  const loadTableData = (
    table: string,
    currentPage: number = page,
    currentPageSize: number = pageSize,
  ) => {
    setSelectedTable(table);
    if (!connectionName.trim()) return;
    const offset = (currentPage - 1) * currentPageSize;
    loadDataMutation.mutate({
      conn: connectionName.trim(),
      table,
      lim: currentPageSize,
      offs: offset,
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">
            Table viewer
          </h2>
          <p className="text-slate-400">Browse tables and view rows</p>
        </div>
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white">Connection &amp; table</CardTitle>
          <CardDescription className="text-slate-400">
            Load tables for a connection, then select a table to view data.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap items-end gap-4">
          <div className="grid gap-2">
            <Label className="text-slate-300">Connection name</Label>
            <input
              className="h-9 w-56 rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100 placeholder:text-slate-500"
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
                  className="h-9 min-w-[180px] rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100"
                  value={selectedTable ?? ""}
                  onChange={(e) => {
                    const t = e.target.value;
                    if (t) {
                      setPage(1);
                      loadTableData(t, 1, pageSize);
                    }
                  }}
                >
                  <option value="">Select table</option>
                  {tables.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              </div>
              {selectedTable && (
                <Button
                  variant="outline"
                  className="border-slate-700 text-slate-300 hover:bg-slate-800"
                  onClick={() => loadTableData(selectedTable, page, pageSize)}
                  disabled={loadDataMutation.isPending}
                >
                  {loadDataMutation.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    "Refresh"
                  )}
                </Button>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {error && (
        <div className="rounded-md border border-red-900/50 bg-red-950/20 px-4 py-2 text-sm text-red-400">
          {error}
        </div>
      )}

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Table2 className="h-4 w-4 text-emerald-500" />
            {selectedTable ?? "Data"}
            {rowCount != null && (
              <span className="text-sm font-normal text-slate-400">
                ({rowCount} total rows, displaying {rows.length})
              </span>
            )}
          </CardTitle>
          <CardDescription className="text-slate-400">
            {selectedTable
              ? `Sample of ${selectedTable}`
              : "Select a table to view data."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loadDataMutation.isPending ? (
            <div className="flex items-center gap-2 text-slate-400 py-8">
              <Loader2 className="h-5 w-5 animate-spin" />
              Loading…
            </div>
          ) : columns.length === 0 && rows.length === 0 ? (
            <p className="text-slate-500 py-4">No data.</p>
          ) : (
            <>
              <ScrollArea className="w-full rounded border border-slate-800">
                <div className="min-w-0 overflow-x-auto">
                  <table className="w-full border-collapse text-sm">
                    <thead>
                      <tr className="border-b border-slate-700 bg-slate-900/50">
                        {columns.map((col) => (
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
                          className={cn(
                            "border-b border-slate-800 hover:bg-slate-800/30",
                            i % 2 === 0 ? "bg-slate-950/30" : "bg-slate-900/20",
                          )}
                        >
                          {columns.map((col) => (
                            <td
                              key={col}
                              className="px-4 py-2 text-slate-300 whitespace-nowrap max-w-[200px] truncate"
                              title={String(
                                (row as Record<string, unknown>)[col] ?? "",
                              )}
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

              <div className="flex items-center justify-between mt-4 pt-4 border-t border-slate-800">
                <div className="flex items-center gap-2 text-sm text-slate-400">
                  <span>Show</span>
                  <select
                    className="h-8 rounded border border-slate-800 bg-slate-900 px-2 text-sm text-slate-200"
                    value={pageSize}
                    onChange={(e) => {
                      const newSize = Number(e.target.value);
                      setPageSize(newSize);
                      setPage(1);
                      if (selectedTable) {
                        loadTableData(selectedTable, 1, newSize);
                      }
                    }}
                  >
                    <option value={10}>10</option>
                    <option value={25}>25</option>
                    <option value={50}>50</option>
                    <option value={100}>100</option>
                  </select>
                  <span>rows per page</span>
                </div>
                <div className="flex items-center gap-4">
                  <Button
                    variant="outline"
                    size="sm"
                    className="border-slate-800 bg-slate-950 text-slate-300 hover:bg-slate-800 hover:text-white"
                    onClick={() => {
                      const prevPage = Math.max(1, page - 1);
                      setPage(prevPage);
                      if (selectedTable) {
                        loadTableData(selectedTable, prevPage, pageSize);
                      }
                    }}
                    disabled={page === 1 || loadDataMutation.isPending}
                  >
                    Previous
                  </Button>
                  <span className="text-sm font-medium text-slate-200">
                    Page {page}{" "}
                    {rowCount !== null &&
                      rowCount > 0 &&
                      `of ${Math.ceil(rowCount / pageSize)}`}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    className="border-slate-800 bg-slate-950 text-slate-300 hover:bg-slate-800 hover:text-white"
                    onClick={() => {
                      const nextPage = page + 1;
                      setPage(nextPage);
                      if (selectedTable) {
                        loadTableData(selectedTable, nextPage, pageSize);
                      }
                    }}
                    disabled={
                      (rowCount !== null && page * pageSize >= rowCount) ||
                      rows.length < pageSize ||
                      loadDataMutation.isPending
                    }
                  >
                    Next
                  </Button>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
