import { useMutation, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, Database, Loader2, RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";
import { callTool } from "@/common/api";
import { cn } from "@/common/utils";
import { Badge } from "@/components/ui/badge";
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

export function Connections() {
  const queryClient = useQueryClient();
  const [supported, setSupported] = useState<Record<string, unknown> | null>(
    null,
  );
  const [listResult, setListResult] = useState<Record<string, unknown> | null>(
    null,
  );
  const [activeResult, setActiveResult] = useState<Record<
    string,
    unknown
  > | null>(null);
  const [testing, setTesting] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const listMutation = useMutation({
    mutationFn: () => callTool("db_connection", { operation: "list" }),
    onSuccess: (data) => {
      setError(null);
      setListResult(extractData(data?.result) ?? null);
    },
    onError: (e: Error) => setError(e.message),
  });

  const activeMutation = useMutation({
    mutationFn: () => callTool("db_connection", { operation: "get_active" }),
    onSuccess: (data) => {
      setError(null);
      setActiveResult(extractData(data?.result) ?? null);
    },
    onError: (e: Error) => setError(e.message),
  });

  const setActiveMutation = useMutation({
    mutationFn: (connection_name: string) =>
      callTool("db_connection", { operation: "set_active", connection_name }),
    onSuccess: () => {
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["connections"] });
      activeMutation.mutate();
    },
    onError: (e: Error) => setError(e.message),
  });

  const testOneMutation = useMutation({
    mutationFn: (connection_name: string) =>
      callTool("db_connection", { operation: "test", connection_name }),
    onSettled: () => setTesting(null),
    onError: (e: Error) => setError(e.message),
  });

  const supportedMutation = useMutation({
    mutationFn: () =>
      callTool("db_connection", { operation: "list_supported" }),
    onSuccess: (data) => {
      setError(null);
      setSupported(extractData(data?.result) ?? null);
    },
    onError: (e: Error) => setError(e.message),
  });

  const connections = listResult?.connections
    ? Object.values(listResult.connections)
    : [];
  const activeName =
    (activeResult?.connection_name as string) ??
    (activeResult?.active as string) ??
    null;

  const refreshAll = () => {
    listMutation.mutate();
    activeMutation.mutate();
  };

  useEffect(() => {
    refreshAll();
    supportedMutation.mutate();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">
            Connections
          </h2>
          <p className="text-slate-400">
            Registered databases and active connection
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            className="border-slate-700 text-slate-300 hover:bg-slate-800"
            onClick={() => supportedMutation.mutate()}
            disabled={supportedMutation.isPending}
          >
            {supportedMutation.isPending ? "Loading..." : "Supported types"}
          </Button>
          <Button
            className="bg-blue-600 hover:bg-blue-700"
            onClick={refreshAll}
            disabled={listMutation.isPending || activeMutation.isPending}
          >
            <RefreshCw
              className={cn(
                "mr-2 h-4 w-4",
                (listMutation.isPending || activeMutation.isPending) &&
                  "animate-spin",
              )}
            />
            Refresh
          </Button>
        </div>
      </div>

      {error && (
        <div className="rounded-md border border-red-900/50 bg-red-950/20 px-4 py-2 text-sm text-red-400">
          {error}
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Database className="h-5 w-5 text-blue-500" />
              Registered connections
            </CardTitle>
            <CardDescription className="text-slate-400">
              {connections.length} connection(s). Set active for Schema / Data
              pages.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[280px] rounded border border-slate-800">
              <ul className="p-2 space-y-1">
                {connections.length === 0 && !listMutation.isPending && (
                  <li className="text-slate-500 text-sm px-2">
                    None. Register via MCP or Tools page.
                  </li>
                )}
                {(connections as unknown[]).map((c, _idx) => {
                  const name =
                    typeof c === "string"
                      ? c
                      : String(
                          (c as Record<string, unknown>).connection_name ??
                            (c as Record<string, unknown>).name ??
                            c,
                        );
                  const isActive = activeName === name;
                  const testingThis = testing === name;
                  return (
                    <li
                      key={name}
                      className={cn(
                        "flex items-center justify-between rounded px-3 py-2 text-sm",
                        isActive
                          ? "bg-slate-800/80 text-white"
                          : "text-slate-300 hover:bg-slate-800/50",
                      )}
                    >
                      <span className="font-mono truncate">{name}</span>
                      <div className="flex items-center gap-1 shrink-0">
                        {isActive && (
                          <Badge className="bg-emerald-900/50 text-emerald-400 border-0 text-xs">
                            Active
                          </Badge>
                        )}
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-7 px-2 text-slate-400 hover:text-white"
                          onClick={() => {
                            if (testingThis) return;
                            setTesting(name);
                            testOneMutation.mutate(name);
                          }}
                          disabled={testingThis}
                        >
                          {testingThis ? (
                            <Loader2 className="h-3 w-3 animate-spin" />
                          ) : (
                            <CheckCircle2 className="h-3 w-3" />
                          )}
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-7 px-2 text-slate-400 hover:text-white"
                          onClick={() => setActiveMutation.mutate(name)}
                          disabled={isActive || setActiveMutation.isPending}
                        >
                          Set active
                        </Button>
                      </div>
                    </li>
                  );
                })}
              </ul>
            </ScrollArea>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white">
              Supported database types
            </CardTitle>
            <CardDescription className="text-slate-400">
              Types available for registration (db_connection register).
            </CardDescription>
          </CardHeader>
          <CardContent>
            {supported && (supported.types as unknown[])?.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {(
                  supported.types as unknown[] as {
                    type?: string;
                    category?: string;
                  }[]
                ).map((t, i) => (
                  <Badge
                    key={i}
                    variant="secondary"
                    className="bg-slate-800 text-slate-300 border-slate-700"
                  >
                    {t.type ?? t.category ?? "?"}
                  </Badge>
                ))}
              </div>
            ) : (
              <p className="text-slate-500 text-sm">
                Click &quot;Supported types&quot; to load.
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
