import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { callTool } from "@/common/api";

type ConnectionConfig = Record<string, string>;

const DB_FIELDS: Record<string, string[]> = {
  sqlite: ["database"],
  postgresql: ["host", "port", "user", "password", "database"],
  mysql: ["host", "port", "user", "password", "database"],
  mongodb: ["host", "port", "database"],
  duckdb: ["database"],
  redis: ["host", "port", "password"],
  lancedb: ["uri", "api_key", "region"],
  chromadb: ["persist_directory", "host", "port"],
};

export function ConnectionManager() {
  const [connectionName, setConnectionName] = useState("");
  const [databaseType, setDatabaseType] = useState("sqlite");
  const [config, setConfig] = useState<ConnectionConfig>({});
  const [result, setResult] = useState<unknown>(null);
  const [error, setError] = useState<string | null>(null);

  const listMutation = useMutation({
    mutationFn: () => callTool("db_connection", { operation: "list" }),
    onSuccess: (res) => {
      setResult(res.result);
      setError(null);
    },
    onError: (e: Error) => setError(e.message),
  });

  const registerMutation = useMutation({
    mutationFn: () =>
      callTool("db_connection", {
        operation: "register",
        connection_name: connectionName,
        database_type: databaseType,
        connection_config: config,
        test_connection: true,
      }),
    onSuccess: (res) => {
      setResult(res.result);
      setError(null);
    },
    onError: (e: Error) => setError(e.message),
  });

  const fieldNames = DB_FIELDS[databaseType] ?? ["database"];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Connection Manager</h2>
        <p className="text-slate-400">Register, list, and validate database connections.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white">Register Connection</CardTitle>
            <CardDescription className="text-slate-400">Uses `db_connection` register operation.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <input
              className="h-10 w-full rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100"
              placeholder="Connection name"
              value={connectionName}
              onChange={(e) => setConnectionName(e.target.value)}
            />
            <select
              className="h-10 w-full rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100"
              value={databaseType}
              onChange={(e) => {
                setDatabaseType(e.target.value);
                setConfig({});
              }}
            >
              {Object.keys(DB_FIELDS).map((db) => (
                <option key={db} value={db}>
                  {db}
                </option>
              ))}
            </select>

            {fieldNames.map((field) => (
              <input
                key={field}
                className="h-10 w-full rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100"
                placeholder={field}
                value={config[field] ?? ""}
                onChange={(e) =>
                  setConfig((prev) => ({
                    ...prev,
                    [field]: e.target.value,
                  }))
                }
              />
            ))}

            <div className="flex gap-2">
              <Button
                className="bg-blue-600 hover:bg-blue-700"
                onClick={() => registerMutation.mutate()}
                disabled={!connectionName.trim() || registerMutation.isPending}
              >
                {registerMutation.isPending ? "Registering..." : "Register + test"}
              </Button>
              <Button
                variant="outline"
                className="border-slate-700 text-slate-300 hover:bg-slate-800"
                onClick={() => listMutation.mutate()}
                disabled={listMutation.isPending}
              >
                {listMutation.isPending ? "Loading..." : "List connections"}
              </Button>
            </div>
            {error && <p className="text-sm text-red-400">{error}</p>}
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white">Result</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="max-h-[520px] overflow-auto rounded border border-slate-800 bg-slate-900/40 p-3 text-xs text-slate-300">
              {JSON.stringify(result ?? { note: "Run an action to see output." }, null, 2)}
            </pre>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
