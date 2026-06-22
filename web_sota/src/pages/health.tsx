import { useMutation } from "@tanstack/react-query";
import { Activity, AlertTriangle, CheckCircle2, Zap } from "lucide-react";
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
import { ScrollArea } from "@/components/ui/scroll-area";

function extractData(res: unknown): Record<string, unknown> | null {
  if (res && typeof res === "object" && "data" in res)
    return (res as { data?: Record<string, unknown> }).data ?? null;
  if (res && typeof res === "object") return res as Record<string, unknown>;
  return null;
}

export function Health() {
  const [connectionName, setConnectionName] = useState("");
  const [connections, setConnections] = useState<{ name: string }[]>([]);
  const [healthResult, setHealthResult] = useState<Record<
    string,
    unknown
  > | null>(null);
  const [metricsResult, setMetricsResult] = useState<Record<
    string,
    unknown
  > | null>(null);
  const [error, setError] = useState<string | null>(null);

  const listMutation = useMutation({
    mutationFn: () => callTool("db_connection", { operation: "list" }),
    onSuccess: (data) => {
      setError(null);
      const d = extractData(data?.result);
      const list =
        (d?.connections as { name?: string; connection_name?: string }[]) ?? [];
      const names = list.map((c) => c.connection_name ?? c.name ?? String(c));
      setConnections(names.map((n) => ({ name: n })));
    },
    onError: (e: Error) => setError(e.message),
  });

  const healthMutation = useMutation({
    mutationFn: (conn: string) =>
      callTool("db_management", {
        operation: "database_health_check",
        connection_name: conn,
        include_metrics: true,
      }),
    onSuccess: (data) => {
      setError(null);
      setHealthResult(extractData(data?.result) ?? null);
    },
    onError: (e: Error) => setError(e.message),
  });

  const metricsMutation = useMutation({
    mutationFn: (conn: string) =>
      callTool("db_management", {
        operation: "get_database_metrics",
        connection_name: conn,
      }),
    onSuccess: (data) => {
      setError(null);
      setMetricsResult(extractData(data?.result) ?? null);
    },
    onError: (e: Error) => setError(e.message),
  });

  const runScan = () => {
    const conn = connectionName.trim();
    if (!conn) {
      setError("Enter or select a connection name.");
      return;
    }
    setHealthResult(null);
    setMetricsResult(null);
    healthMutation.mutate(conn);
    metricsMutation.mutate(conn);
  };

  const status = healthResult?.status ?? healthResult?.healthy;
  const healthy =
    status === "ok" || status === true || healthResult?.success === true;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">
            Health &amp; Diagnostics
          </h2>
          <p className="text-slate-400">Database health check and metrics</p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            className="border-slate-700 text-slate-300 hover:bg-slate-800"
            onClick={() => listMutation.mutate()}
            disabled={listMutation.isPending}
          >
            {listMutation.isPending ? "Loading..." : "List connections"}
          </Button>
          <Button
            className="bg-emerald-600 hover:bg-emerald-700 text-white"
            onClick={runScan}
            disabled={
              !connectionName.trim() ||
              healthMutation.isPending ||
              metricsMutation.isPending
            }
          >
            <Zap className="mr-2 h-4 w-4" />
            {healthMutation.isPending || metricsMutation.isPending
              ? "Running..."
              : "Run health check"}
          </Button>
        </div>
      </div>

      {error && (
        <div className="rounded-md border border-red-900/50 bg-red-950/20 px-4 py-2 text-sm text-red-400">
          {error}
        </div>
      )}

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white">Connection</CardTitle>
          <CardDescription className="text-slate-400">
            Pick a registered connection to run health check and metrics.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap items-center gap-4">
          <input
            className="h-9 w-64 rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100 placeholder:text-slate-500"
            value={connectionName}
            onChange={(e) => setConnectionName(e.target.value)}
            placeholder="Connection name"
            list="health-connections-list"
          />
          <datalist id="health-connections-list">
            {connections.map((c) => (
              <option key={c.name} value={c.name} />
            ))}
          </datalist>
        </CardContent>
      </Card>

      {(healthResult != null || metricsResult != null) && (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-400">
                Status
              </CardTitle>
              {healthy ? (
                <CheckCircle2 className="h-4 w-4 text-emerald-500" />
              ) : (
                <AlertTriangle className="h-4 w-4 text-amber-500" />
              )}
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-slate-200">
                {healthy ? "Healthy" : "Check result"}
              </div>
              <p className="text-xs text-slate-500 mt-1">
                {(healthResult?.message as string) ??
                  (healthy ? "Connection OK" : "See details below")}
              </p>
            </CardContent>
          </Card>
          <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-400">
                Metrics
              </CardTitle>
              <Activity className="h-4 w-4 text-blue-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-slate-200">
                {metricsResult ? "Available" : "—"}
              </div>
              <p className="text-xs text-slate-500 mt-1">
                Performance and usage
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-slate-200">
              Health check result
            </CardTitle>
            <CardDescription className="text-slate-500">
              database_health_check output
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[200px] rounded border border-slate-800">
              <pre className="p-3 text-xs text-slate-300 whitespace-pre-wrap break-all font-mono">
                {healthResult != null
                  ? JSON.stringify(healthResult, null, 2)
                  : "Run health check to see result."}
              </pre>
            </ScrollArea>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-slate-200">Database metrics</CardTitle>
            <CardDescription className="text-slate-500">
              get_database_metrics output
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[200px] rounded border border-slate-800">
              <pre className="p-3 text-xs text-slate-300 whitespace-pre-wrap break-all font-mono">
                {metricsResult != null
                  ? JSON.stringify(metricsResult, null, 2)
                  : "Run health check to see metrics."}
              </pre>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
