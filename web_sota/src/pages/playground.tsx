import { useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { callTool, getTools } from "@/common/api";

type HistoryItem = {
  id: string;
  tool: string;
  args: string;
  ok: boolean;
  result: unknown;
  at: string;
};

export function Playground() {
  const [selected, setSelected] = useState("");
  const [argsJson, setArgsJson] = useState("{}");
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);

  const toolsQuery = useQuery({ queryKey: ["tools"], queryFn: getTools });
  const tools = toolsQuery.data?.tools ?? [];

  const selectedTool = useMemo(
    () => tools.find((t) => t.name === selected),
    [tools, selected],
  );

  const callMutation = useMutation({
    mutationFn: ({ name, args }: { name: string; args: Record<string, unknown> }) => callTool(name, args),
    onSuccess: (data, vars) => {
      setError(null);
      setHistory((prev) => [
        {
          id: `${Date.now()}-${vars.name}`,
          tool: vars.name,
          args: JSON.stringify(vars.args, null, 2),
          ok: !data.isError,
          result: data.result,
          at: new Date().toISOString(),
        },
        ...prev.slice(0, 19),
      ]);
    },
    onError: (e: Error) => setError(e.message),
  });

  const run = () => {
    if (!selected) {
      setError("Select a tool first.");
      return;
    }
    try {
      const parsed = JSON.parse(argsJson || "{}") as Record<string, unknown>;
      callMutation.mutate({ name: selected, args: parsed });
    } catch {
      setError("Arguments must be valid JSON.");
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Playground</h2>
        <p className="text-slate-400">Run tools, inspect outputs, keep reproducible history.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white">Call Tool</CardTitle>
            <CardDescription className="text-slate-400">Ad-hoc execution from the webapp.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <select
              className="h-10 w-full rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100"
              value={selected}
              onChange={(e) => setSelected(e.target.value)}
            >
              <option value="">Select tool...</option>
              {tools.map((t) => (
                <option key={t.name} value={t.name}>
                  {t.name}
                </option>
              ))}
            </select>

            {selectedTool && (
              <p className="text-sm text-slate-400 whitespace-pre-wrap">{selectedTool.description || "No description"}</p>
            )}

            <textarea
              className="min-h-[180px] w-full rounded-md border border-slate-800 bg-slate-900 p-3 font-mono text-sm text-slate-100"
              value={argsJson}
              onChange={(e) => setArgsJson(e.target.value)}
            />

            {error && <p className="text-sm text-red-400">{error}</p>}

            {callMutation.data && (
              <div className="rounded border border-slate-800 bg-slate-900/50 p-3">
                <p className="mb-1 text-xs text-slate-500">Latest result</p>
                <pre className="text-xs text-slate-300 whitespace-pre-wrap break-all">
                  {JSON.stringify(callMutation.data.result, null, 2)}
                </pre>
              </div>
            )}

            <Button className="bg-blue-600 hover:bg-blue-700" onClick={run} disabled={callMutation.isPending}>
              {callMutation.isPending ? "Running..." : "Run"}
            </Button>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white">History</CardTitle>
            <CardDescription className="text-slate-400">Last 20 invocations in this session.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {history.length === 0 && <p className="text-sm text-slate-500">No calls yet.</p>}
            {history.map((h) => (
              <div key={h.id} className="rounded border border-slate-800 bg-slate-900/30 p-3">
                <div className="flex items-center justify-between">
                  <p className="font-mono text-sm text-slate-100">{h.tool}</p>
                  <p className={h.ok ? "text-xs text-emerald-400" : "text-xs text-amber-400"}>
                    {h.ok ? "ok" : "error"}
                  </p>
                </div>
                <p className="mt-1 text-xs text-slate-500">{h.at}</p>
                <details className="mt-2">
                  <summary className="cursor-pointer text-xs text-slate-400">Args / result</summary>
                  <pre className="mt-2 text-xs text-slate-300 whitespace-pre-wrap break-all">
                    {h.args}
                    {"\n\n"}
                    {JSON.stringify(h.result, null, 2)}
                  </pre>
                </details>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
