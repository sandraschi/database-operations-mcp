import { useMutation } from "@tanstack/react-query";
import { Play, Table2 } from "lucide-react";
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

export function Data() {
  const [connectionName, setConnectionName] = useState("");
  const [query, setQuery] = useState("SELECT 1");
  const [tableName, setTableName] = useState("");
  const [sampleLimit, setSampleLimit] = useState(10);
  const [result, setResult] = useState<unknown>(null);
  const [error, setError] = useState<string | null>(null);

  const queryMutation = useMutation({
    mutationFn: ({ conn, sql }: { conn: string; sql: string }) =>
      callTool("db_operations", {
        operation: "execute_query",
        connection_name: conn,
        query: sql,
        limit: 500,
      }),
    onSuccess: (data) => {
      setError(null);
      const d = extractData(data?.result);
      setResult(d ?? data?.result);
    },
    onError: (e: Error) => setError(e.message),
  });

  const sampleMutation = useMutation({
    mutationFn: ({
      conn,
      table,
      limit,
    }: {
      conn: string;
      table: string;
      limit: number;
    }) =>
      callTool("db_operations", {
        operation: "quick_data_sample",
        connection_name: conn,
        table_name: table,
        limit,
      }),
    onSuccess: (data) => {
      setError(null);
      const d = extractData(data?.result);
      setResult(d ?? data?.result);
    },
    onError: (e: Error) => setError(e.message),
  });

  const runQuery = () => {
    if (!connectionName.trim()) {
      setError("Enter connection name.");
      return;
    }
    if (!query.trim()) {
      setError("Enter a query.");
      return;
    }
    queryMutation.mutate({ conn: connectionName.trim(), sql: query.trim() });
  };

  const runSample = () => {
    if (!connectionName.trim()) {
      setError("Enter connection name.");
      return;
    }
    if (!tableName.trim()) {
      setError("Enter table name.");
      return;
    }
    sampleMutation.mutate({
      conn: connectionName.trim(),
      table: tableName.trim(),
      limit: sampleLimit,
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Data</h2>
        <p className="text-slate-400">Run queries and quick table samples</p>
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white">Connection</CardTitle>
          <CardDescription className="text-slate-400">
            Same connection name as in Connections / Schema.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-2 max-w-xs">
            <Label className="text-slate-300">Connection name</Label>
            <input
              className="h-9 rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100 placeholder:text-slate-500"
              value={connectionName}
              onChange={(e) => setConnectionName(e.target.value)}
              placeholder="e.g. local_sqlite"
            />
          </div>
        </CardContent>
      </Card>

      {error && (
        <div className="rounded-md border border-red-900/50 bg-red-950/20 px-4 py-2 text-sm text-red-400">
          {error}
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Play className="h-4 w-4 text-blue-500" />
              Execute query
            </CardTitle>
            <CardDescription className="text-slate-400">
              Read-only SQL (SELECT). Limit 500 rows.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-2">
              <Label className="text-slate-300">SQL</Label>
              <textarea
                className="min-h-[120px] w-full rounded-md border border-slate-800 bg-slate-900 p-3 font-mono text-sm text-slate-100 placeholder:text-slate-500"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="SELECT * FROM ..."
              />
            </div>
            <Button
              className="bg-blue-600 hover:bg-blue-700"
              onClick={runQuery}
              disabled={
                queryMutation.isPending ||
                !connectionName.trim() ||
                !query.trim()
              }
            >
              {queryMutation.isPending ? "Running..." : "Run query"}
            </Button>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Table2 className="h-4 w-4 text-emerald-500" />
              Quick sample
            </CardTitle>
            <CardDescription className="text-slate-400">
              Sample rows from a table.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-2">
              <Label className="text-slate-300">Table name</Label>
              <input
                className="h-9 w-full rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100 placeholder:text-slate-500"
                value={tableName}
                onChange={(e) => setTableName(e.target.value)}
                placeholder="e.g. users"
              />
            </div>
            <div className="grid gap-2">
              <Label className="text-slate-300">Limit</Label>
              <input
                type="number"
                min={1}
                max={1000}
                className="h-9 w-24 rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100"
                value={sampleLimit}
                onChange={(e) => setSampleLimit(Number(e.target.value) || 10)}
              />
            </div>
            <Button
              className="bg-emerald-600 hover:bg-emerald-700"
              onClick={runSample}
              disabled={
                sampleMutation.isPending ||
                !connectionName.trim() ||
                !tableName.trim()
              }
            >
              {sampleMutation.isPending ? "Loading..." : "Sample table"}
            </Button>
          </CardContent>
        </Card>
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white">Result</CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[320px] rounded border border-slate-800 bg-slate-900/30">
            <pre className="p-4 text-xs text-slate-300 whitespace-pre-wrap break-all font-mono">
              {result != null
                ? JSON.stringify(result, null, 2)
                : "Run a query or sample to see results."}
            </pre>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}
