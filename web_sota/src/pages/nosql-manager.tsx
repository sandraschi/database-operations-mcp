import {
  AlertCircle,
  Clock,
  Database,
  Hash,
  Loader2,
  RefreshCw,
  Search,
  Trash2,
} from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { callTool } from "@/common/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

interface RedisConnection {
  name: string;
  type: string;
  status: string;
  connected: boolean;
}

interface RedisKey {
  name: string;
  type: string;
  ttl: number;
  value: string | null;
}

function extractData(res: unknown): Record<string, unknown> | null {
  if (res && typeof res === "object" && "data" in res)
    return (res as { data?: Record<string, unknown> }).data ?? null;
  if (res && typeof res === "object") return res as Record<string, unknown>;
  return null;
}

async function callRedisOp(
  connectionName: string,
  operation: string,
  args: Record<string, unknown> = {},
) {
  const res = await callTool("db_operations_extended", {
    database_type: "redis",
    connection_name: connectionName,
    operation,
    ...args,
  });
  return extractData(res.result);
}

function formatTtl(seconds: number): string {
  if (seconds === -1) return "Persistent";
  if (seconds === -2) return "Expired";
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export function NoSQLManager() {
  const [connections, setConnections] = useState<RedisConnection[]>([]);
  const [connectionName, setConnectionName] = useState<string | null>(null);
  const [connectionsLoading, setConnectionsLoading] = useState(true);
  const [filter, setFilter] = useState("*");
  const [keys, setKeys] = useState<RedisKey[]>([]);
  const [scanning, setScanning] = useState(false);
  const [flushing, setFlushing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadConnections = async () => {
    setConnectionsLoading(true);
    setError(null);
    try {
      const res = await callTool("db_connection", { operation: "list" });
      const data = extractData(res.result);
      const list = data?.connections
        ? (Object.values(data.connections) as RedisConnection[])
        : [];
      const redisConnections = list.filter((c) => c.type === "redis");
      setConnections(redisConnections);
      setConnectionName((prev) =>
        prev && redisConnections.some((c) => c.name === prev)
          ? prev
          : (redisConnections[0]?.name ?? null),
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load connections");
    } finally {
      setConnectionsLoading(false);
    }
  };

  useEffect(() => {
    loadConnections();
  }, []);

  const scan = async () => {
    if (!connectionName) return;
    setScanning(true);
    setError(null);
    try {
      const scanResult = await callRedisOp(connectionName, "get_keys", {
        key: filter || "*",
      });
      if (scanResult?.success === false) {
        setError((scanResult.message as string) ?? "SCAN failed");
        setKeys([]);
        return;
      }
      const rows = (scanResult?.result as Array<Record<string, unknown>>) ?? [];
      const keyNames = rows
        .map((r) => (r.item as string) ?? (r.result as string))
        .filter(Boolean);

      const details = await Promise.all(
        keyNames.slice(0, 50).map(async (name) => {
          const [typeRes, ttlRes] = await Promise.all([
            callRedisOp(connectionName, "get_type", { key: name }),
            callRedisOp(connectionName, "get_ttl", { key: name }),
          ]);
          const type =
            ((typeRes?.result as Array<Record<string, unknown>>)?.[0]
              ?.result as string) ?? "unknown";
          const ttl =
            ((ttlRes?.result as Array<Record<string, unknown>>)?.[0]
              ?.result as number) ?? -1;

          let value: string | null = null;
          if (type === "string") {
            const valRes = await callRedisOp(connectionName, "get_value", {
              key: name,
            });
            value =
              ((valRes?.result as Array<Record<string, unknown>>)?.[0]
                ?.result as string) ?? null;
          }

          return { name, type, ttl, value };
        }),
      );

      setKeys(details);
    } catch (e) {
      setError(e instanceof Error ? e.message : "SCAN failed");
    } finally {
      setScanning(false);
    }
  };

  const deleteKey = async (name: string) => {
    if (!connectionName) return;
    try {
      await callRedisOp(connectionName, "delete_key", { key: name });
      setKeys((prev) => prev.filter((k) => k.name !== name));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to delete key");
    }
  };

  const flushCache = async () => {
    if (!connectionName) return;
    if (
      !window.confirm(
        `Flush all keys on connection "${connectionName}"? This cannot be undone.`,
      )
    ) {
      return;
    }
    setFlushing(true);
    setError(null);
    try {
      await callRedisOp(connectionName, "flush");
      setKeys([]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Flush failed");
    } finally {
      setFlushing(false);
    }
  };

  if (connectionsLoading) {
    return (
      <div
        className="flex items-center justify-center h-64 text-slate-500 gap-2"
        data-testid="nosql-manager-page"
      >
        <Loader2 className="h-5 w-5 animate-spin" />
        Loading connections...
      </div>
    );
  }

  if (connections.length === 0) {
    return (
      <div className="space-y-6" data-testid="nosql-manager-page">
        <h2
          className="text-2xl font-bold tracking-tight text-white"
          data-testid="nosql-manager-heading"
        >
          NoSQL Manager
        </h2>
        <Card className="border-slate-800 bg-slate-900/50">
          <CardContent className="p-8 text-center text-slate-400 space-y-3">
            <Database className="h-10 w-10 mx-auto text-slate-600" />
            <p>No Redis connection is registered.</p>
            <p className="text-sm text-slate-500">
              Add one on the{" "}
              <Link to="/connections" className="text-blue-400 hover:underline">
                Connections
              </Link>{" "}
              page, then come back here.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="nosql-manager-page">
      <div className="flex items-center justify-between">
        <div>
          <h2
            className="text-2xl font-bold tracking-tight text-white"
            data-testid="nosql-manager-heading"
          >
            NoSQL Manager
          </h2>
          <p className="text-slate-400">
            Browse and manage Redis key-value stores
            {connections.length > 1 && connectionName && (
              <>
                {" "}
                &mdash;{" "}
                <select
                  value={connectionName}
                  onChange={(e) => setConnectionName(e.target.value)}
                  className="bg-slate-900 border border-slate-800 rounded px-1 text-slate-300 text-sm"
                >
                  {connections.map((c) => (
                    <option key={c.name} value={c.name}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </>
            )}
            {connections.length === 1 && ` — ${connectionName}`}
          </p>
        </div>
        <Button
          variant="outline"
          className="border-slate-800 bg-slate-900/50 hover:bg-slate-800"
          onClick={flushCache}
          disabled={flushing}
          data-testid="nosql-manager-flush-button"
        >
          {flushing ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <RefreshCw className="mr-2 h-4 w-4" />
          )}
          Flush Cache
        </Button>
      </div>

      {error && (
        <div className="flex items-center gap-2 text-red-400 text-sm bg-red-400/10 p-3 rounded border border-red-400/20">
          <AlertCircle className="h-4 w-4 shrink-0" />
          {error}
        </div>
      )}

      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
          <Input
            placeholder="Filter keys (e.g. user:*)"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && scan()}
            className="pl-10 bg-slate-950 border-slate-800 focus:ring-blue-500"
            data-testid="nosql-manager-filter-input"
          />
        </div>
        <Button
          className="bg-blue-600 hover:bg-blue-700 text-white"
          onClick={scan}
          disabled={scanning}
          data-testid="nosql-manager-scan-button"
        >
          {scanning ? <Loader2 className="h-4 w-4 animate-spin" /> : "SCAN"}
        </Button>
      </div>

      <div className="grid gap-4">
        {keys.length === 0 ? (
          <div className="p-8 text-center text-slate-600 text-sm italic">
            {scanning ? "Scanning..." : "No keys loaded. Run SCAN to browse."}
          </div>
        ) : (
          keys.map((k) => (
            <KeyItem
              key={k.name}
              keyData={k}
              onDelete={() => deleteKey(k.name)}
            />
          ))
        )}
      </div>
    </div>
  );
}

function KeyItem({
  keyData,
  onDelete,
}: {
  keyData: RedisKey;
  onDelete: () => void;
}) {
  const { name, type, ttl, value } = keyData;
  return (
    <Card className="border-slate-800 bg-slate-950/50 hover:bg-slate-900/50 transition-colors">
      <CardContent className="p-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="bg-slate-900 p-2 rounded border border-slate-800">
            <Database className="h-4 w-4 text-blue-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-sm font-bold text-slate-200">
                {name}
              </span>
              <Badge
                variant="outline"
                className="text-[10px] uppercase border-slate-700 text-slate-400 h-4"
              >
                {type}
              </Badge>
            </div>
            <div className="flex items-center gap-3 mt-1 text-xs text-slate-500">
              <div className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                <span>TTL: {formatTtl(ttl)}</span>
              </div>
              <div className="flex items-center gap-1">
                <Hash className="h-3 w-3" />
                <span>{value ?? `[${type}]`}</span>
              </div>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <Button
            variant="ghost"
            size="icon"
            className="hover:bg-red-900/20 hover:text-red-500 h-8 w-8"
            onClick={onDelete}
            data-testid={`nosql-manager-delete-${name}`}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
