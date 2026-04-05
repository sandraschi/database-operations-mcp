import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { callTool } from "@/common/api";

type Job = {
  id: string;
  type: string;
  status: "pending" | "running" | "done" | "error";
  payload: Record<string, unknown>;
  result?: unknown;
  error?: string;
};

export function JobsExports() {
  const [connectionName, setConnectionName] = useState("");
  const [query, setQuery] = useState("SELECT 1 as ok");
  const [outputPath, setOutputPath] = useState("");
  const [jobs, setJobs] = useState<Job[]>([]);

  const exportMutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => callTool("db_operations", payload),
    onMutate: (payload) => {
      const id = `${Date.now()}-export`;
      setJobs((prev) => [{ id, type: "db-export", status: "running", payload }, ...prev]);
      return { id };
    },
    onSuccess: (data, _vars, ctx) => {
      setJobs((prev) =>
        prev.map((j) =>
          j.id === ctx?.id ? { ...j, status: "done", result: data.result } : j,
        ),
      );
    },
    onError: (e: Error, _vars, ctx) => {
      setJobs((prev) =>
        prev.map((j) =>
          j.id === ctx?.id ? { ...j, status: "error", error: e.message } : j,
        ),
      );
    },
  });

  const startExport = () => {
    const payload: Record<string, unknown> = {
      operation: "export_query_results",
      connection_name: connectionName,
      query,
      output_format: outputPath.toLowerCase().endsWith(".csv") ? "csv" : "json",
    };
    if (outputPath.trim()) payload.output_path = outputPath.trim();
    exportMutation.mutate(payload);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Jobs & Exports</h2>
        <p className="text-slate-400">Track export-oriented jobs and inspect responses.</p>
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white">New Export Job</CardTitle>
          <CardDescription className="text-slate-400">
            Uses `db_operations(operation=&quot;export_query_results&quot;)`.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <input
            className="h-10 w-full rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100"
            placeholder="Connection name"
            value={connectionName}
            onChange={(e) => setConnectionName(e.target.value)}
          />
          <textarea
            className="min-h-[120px] w-full rounded-md border border-slate-800 bg-slate-900 p-3 font-mono text-sm text-slate-100"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <input
            className="h-10 w-full rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100"
            placeholder="Output path (optional). Example: C:/tmp/export.json"
            value={outputPath}
            onChange={(e) => setOutputPath(e.target.value)}
          />
          <Button
            className="bg-blue-600 hover:bg-blue-700"
            onClick={startExport}
            disabled={!connectionName.trim() || exportMutation.isPending}
          >
            {exportMutation.isPending ? "Starting..." : "Start export"}
          </Button>
        </CardContent>
      </Card>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white">Job History</CardTitle>
          <CardDescription className="text-slate-400">Most recent jobs first.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {jobs.length === 0 && <p className="text-sm text-slate-500">No jobs yet.</p>}
          {jobs.map((job) => (
            <div key={job.id} className="rounded border border-slate-800 bg-slate-900/30 p-3">
              <div className="flex items-center justify-between">
                <p className="font-mono text-sm text-slate-100">{job.id}</p>
                <p className="text-xs text-slate-400">{job.status}</p>
              </div>
              <pre className="mt-2 text-xs text-slate-300 whitespace-pre-wrap break-all">
                {JSON.stringify(job.payload, null, 2)}
              </pre>
              {job.result != null && (
                <pre className="mt-2 text-xs text-emerald-300 whitespace-pre-wrap break-all">
                  {JSON.stringify(job.result, null, 2)}
                </pre>
              )}
              {job.error && <p className="mt-2 text-xs text-red-400">{job.error}</p>}
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
