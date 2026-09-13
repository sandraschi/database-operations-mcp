import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Activity,
  ArrowRight,
  Brain,
  Database,
  FileText,
  MessageSquare,
  Plug,
  RefreshCw,
  ScrollText,
  Search,
  Settings,
  ShieldCheck,
  Table,
  Wrench,
} from "lucide-react";
import { Link } from "react-router-dom";
import {
  callTool,
  getCapabilities,
  getHealth,
  getLogStats,
  getTools,
  queryLogs,
} from "@/common/api";
import { cn } from "@/common/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { API_BASE } from "@/lib/api";

function extractData(res: unknown): Record<string, unknown> | null {
  if (res && typeof res === "object" && "data" in res) {
    return (res as { data?: Record<string, unknown> }).data ?? null;
  }
  if (res && typeof res === "object") {
    return res as Record<string, unknown>;
  }
  return null;
}

function asRecord(value: unknown): Record<string, unknown> | null {
  if (value && typeof value === "object" && !Array.isArray(value)) {
    return value as Record<string, unknown>;
  }
  return null;
}

function asString(value: unknown): string | null {
  return typeof value === "string" && value.length > 0 ? value : null;
}

interface LlmSettings {
  provider: string | null;
  model: string | null;
}

async function getLlmSettings(): Promise<LlmSettings> {
  const r = await fetch(`${API_BASE}/api/v1/settings/llm`);
  if (!r.ok) {
    throw new Error(`LLM settings failed: ${r.status}`);
  }
  const body = (await r.json()) as Record<string, unknown>;
  return {
    provider: asString(body.provider),
    model: asString(body.model),
  };
}

const QUICK_ACTIONS = [
  {
    to: "/chat",
    label: "AI Chat",
    desc: "Ask about your data",
    icon: MessageSquare,
  },
  {
    to: "/connections",
    label: "Connections",
    desc: "Manage database links",
    icon: Plug,
  },
  {
    to: "/simple-query",
    label: "Quick Query",
    desc: "Run SQL in seconds",
    icon: Search,
  },
  {
    to: "/db-browser",
    label: "DB Browser",
    desc: "Browse tables live",
    icon: Table,
  },
  { to: "/schema", label: "Schema", desc: "Inspect structure", icon: Database },
  {
    to: "/playground",
    label: "Playground",
    desc: "Try any MCP tool",
    icon: Wrench,
  },
  { to: "/logs", label: "Logs", desc: "Activity + exports", icon: ScrollText },
  {
    to: "/settings",
    label: "Settings",
    desc: "Providers + LLM",
    icon: Settings,
  },
];

const LEVEL_STYLE: Record<string, string> = {
  error: "text-red-400",
  warning: "text-amber-400",
  warn: "text-amber-400",
  info: "text-sky-400",
  debug: "text-slate-500",
  success: "text-emerald-400",
};

export function Dashboard() {
  const queryClient = useQueryClient();

  const healthQuery = useQuery({
    queryKey: ["health"],
    queryFn: getHealth,
    refetchInterval: 15_000,
  });
  const toolsQuery = useQuery({ queryKey: ["tools"], queryFn: getTools });
  const capsQuery = useQuery({
    queryKey: ["capabilities"],
    queryFn: getCapabilities,
  });
  const logStatsQuery = useQuery({
    queryKey: ["log-stats"],
    queryFn: getLogStats,
    refetchInterval: 15_000,
  });
  const recentLogsQuery = useQuery({
    queryKey: ["recent-logs"],
    queryFn: () => queryLogs({ limit: 8, sort: "desc" }),
    refetchInterval: 10_000,
  });
  const connectionsQuery = useQuery({
    queryKey: ["dashboard-connections"],
    queryFn: async () => {
      const res = await callTool("db_connection", { operation: "list" });
      return extractData(res.result);
    },
    enabled: healthQuery.data?.status === "ok",
  });
  const activeQuery = useQuery({
    queryKey: ["dashboard-active"],
    queryFn: async () => {
      const res = await callTool("db_connection", { operation: "get_active" });
      return extractData(res.result);
    },
    enabled: healthQuery.data?.status === "ok",
  });
  const supportedQuery = useQuery({
    queryKey: ["dashboard-supported"],
    queryFn: async () => {
      const res = await callTool("db_connection", {
        operation: "list_supported",
      });
      return extractData(res.result);
    },
    enabled: healthQuery.data?.status === "ok",
    staleTime: Infinity,
  });
  const llmQuery = useQuery({
    queryKey: ["dashboard-llm"],
    queryFn: getLlmSettings,
    enabled: healthQuery.data?.status === "ok",
    retry: false,
  });

  const healthy = healthQuery.data?.status === "ok";
  const loading = healthQuery.isLoading || toolsQuery.isLoading;
  const error = healthQuery.error ?? toolsQuery.error;

  const toolCount = toolsQuery.data?.tools?.length ?? 0;
  const surface = capsQuery.data?.tool_surface;
  const portmanteauCount = surface?.portmanteau_count ?? 0;
  const atomicCount = surface?.atomic_count ?? 0;
  const surfaceTotal = portmanteauCount + atomicCount;
  const portmanteauPct =
    surfaceTotal > 0 ? Math.round((portmanteauCount / surfaceTotal) * 100) : 0;

  const connectionsRecord = connectionsQuery.data?.connections;
  const connectionList: Record<string, unknown>[] = connectionsRecord
    ? Object.values(asRecord(connectionsRecord) ?? {})
        .map(asRecord)
        .filter((c): c is Record<string, unknown> => c !== null)
    : [];
  const activeName =
    asString(activeQuery.data?.connection_name) ??
    asString(activeQuery.data?.active);

  const supported = supportedQuery.data;
  const dbByCategory = asRecord(supported?.databases_by_category);
  const enginesByCategory: {
    category: string;
    engines: { name: string; type: string }[];
  }[] = [];
  if (dbByCategory) {
    for (const [category, list] of Object.entries(dbByCategory)) {
      if (!Array.isArray(list)) {
        continue;
      }
      const engines: { name: string; type: string }[] = [];
      for (const item of list) {
        const rec = asRecord(item);
        const name = rec ? (asString(rec.name) ?? asString(rec.type)) : null;
        const type = rec ? asString(rec.type) : null;
        if (name && type) {
          engines.push({ name, type });
        }
      }
      if (engines.length > 0) {
        enginesByCategory.push({ category, engines });
      }
    }
  }
  const engineTotalRaw = supported?.total_supported;
  const engineTotal =
    typeof engineTotalRaw === "number"
      ? engineTotalRaw
      : enginesByCategory.reduce((n, g) => n + g.engines.length, 0);

  const logTotal = logStatsQuery.data?.total ?? null;
  const recentEntries = recentLogsQuery.data?.entries ?? [];

  const refreshAll = () => {
    void queryClient.invalidateQueries();
  };

  return (
    <div className="space-y-6">
      {/* Hero */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">
            Database Operations
          </h2>
          <p className="text-slate-400">
            Live overview of engines, connections, tools and activity
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Badge
            data-testid="service-status"
            className={cn(
              "gap-1.5 px-3 py-1 text-xs",
              healthy
                ? "border-emerald-800 bg-emerald-950 text-emerald-300"
                : "border-red-800 bg-red-950 text-red-300",
            )}
          >
            <span className="relative flex h-2 w-2">
              <span
                className={cn(
                  "absolute inline-flex h-full w-full animate-ping rounded-full opacity-60",
                  healthy ? "bg-emerald-400" : "bg-red-400",
                )}
              />
              <span
                className={cn(
                  "relative inline-flex h-2 w-2 rounded-full",
                  healthy ? "bg-emerald-400" : "bg-red-400",
                )}
              />
            </span>
            {healthQuery.isLoading
              ? "Checking..."
              : healthy
                ? "Online :10709"
                : "Offline"}
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={refreshAll}
            className="border-slate-700 text-slate-300"
          >
            <RefreshCw className="mr-2 h-3.5 w-3.5" />
            Refresh
          </Button>
        </div>
      </div>

      {error && (
        <Card className="border-red-900 bg-red-950/30">
          <CardContent className="pt-4 text-sm text-red-300">
            Backend unreachable: {String(error)}. Start it with{" "}
            <code className="font-mono">just serve</code> (port 10709).
          </CardContent>
        </Card>
      )}

      {/* KPI cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              Service
            </CardTitle>
            <ShieldCheck
              className={cn(
                "h-4 w-4",
                healthy ? "text-emerald-500" : "text-red-500",
              )}
            />
          </CardHeader>
          <CardContent>
            <div
              data-testid="kpi-service"
              className="text-2xl font-bold text-white"
            >
              {loading ? "..." : healthy ? "Online" : "Offline"}
            </div>
            <p className="text-xs text-slate-400">
              {healthQuery.data?.mcp
                ? "MCP mounted"
                : "Single process MCP+REST"}
            </p>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              MCP Tools
            </CardTitle>
            <Wrench className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div
              data-testid="kpi-tools"
              className="text-2xl font-bold text-white"
            >
              {loading ? "..." : toolCount}
            </div>
            <p className="text-xs text-slate-400">
              {portmanteauCount > 0
                ? `${portmanteauCount} portmanteau / ${atomicCount} atomic`
                : "Across SQL, NoSQL, vector"}
            </p>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              Connections
            </CardTitle>
            <Plug className="h-4 w-4 text-cyan-500" />
          </CardHeader>
          <CardContent>
            <div
              data-testid="kpi-connections"
              className="text-2xl font-bold text-white"
            >
              {!healthy
                ? "-"
                : connectionsQuery.isLoading
                  ? "..."
                  : connectionList.length}
            </div>
            <p className="text-xs text-slate-400">
              {activeName ? `Active: ${activeName}` : "No active connection"}
            </p>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              Engines
            </CardTitle>
            <Database className="h-4 w-4 text-violet-500" />
          </CardHeader>
          <CardContent>
            <div
              data-testid="kpi-engines"
              className="text-2xl font-bold text-white"
            >
              {!healthy ? "-" : supportedQuery.isLoading ? "..." : engineTotal}
            </div>
            <p className="text-xs text-slate-400">Supported database types</p>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              Log Events
            </CardTitle>
            <Activity className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div
              data-testid="kpi-logs"
              className="text-2xl font-bold text-white"
            >
              {logTotal ?? (healthy ? "..." : "-")}
            </div>
            <p className="text-xs text-slate-400">
              Ring buffer, live feed below
            </p>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              AI Chat
            </CardTitle>
            <Brain className="h-4 w-4 text-pink-500" />
          </CardHeader>
          <CardContent>
            <div
              data-testid="kpi-llm"
              className="text-2xl font-bold text-white"
            >
              {llmQuery.data?.provider
                ? llmQuery.data.provider
                : llmQuery.isLoading
                  ? "..."
                  : "Unset"}
            </div>
            <p className="text-xs text-slate-400">
              {llmQuery.data?.model ?? "Configure in Settings"}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Activity + side column */}
      <div className="grid gap-4 lg:grid-cols-7">
        <Card className="border-slate-800 bg-slate-950/50 lg:col-span-4">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-white">Live activity</CardTitle>
            <Link
              to="/logs"
              className="flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200"
            >
              Full logs <ArrowRight className="h-3 w-3" />
            </Link>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] space-y-1.5 overflow-y-auto rounded-md border border-slate-800 bg-slate-900/50 p-4 font-mono text-xs">
              {recentLogsQuery.isLoading && (
                <p className="text-blue-400">
                  [system] Tailing backend logs...
                </p>
              )}
              {!healthy && !recentLogsQuery.isLoading && (
                <p className="text-slate-500">
                  [idle] Backend offline - feed resumes on reconnect.
                </p>
              )}
              {recentEntries.map((entry) => (
                <p key={entry.id} className="break-words text-slate-400">
                  <span className="text-slate-600">
                    {entry.timestamp.slice(11, 19)}
                  </span>{" "}
                  <span
                    className={cn(
                      LEVEL_STYLE[entry.level.toLowerCase()] ??
                        "text-slate-300",
                    )}
                  >
                    [{entry.level}]
                  </span>{" "}
                  <span className="text-slate-500">[{entry.kind}]</span>{" "}
                  {entry.detail}
                </p>
              ))}
              {healthy &&
                !recentLogsQuery.isLoading &&
                recentEntries.length === 0 && (
                  <p className="text-slate-500">
                    [idle] No events yet - run a query or test a connection.
                  </p>
                )}
            </div>
          </CardContent>
        </Card>

        <div className="space-y-4 lg:col-span-3">
          <Card className="border-slate-800 bg-slate-950/50">
            <CardHeader>
              <CardTitle className="text-white">Quick actions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-2">
                {QUICK_ACTIONS.map((action) => (
                  <Link
                    key={action.to}
                    to={action.to}
                    className="group flex items-start gap-2.5 rounded-md border border-slate-800 bg-slate-900/50 p-3 transition-colors hover:border-slate-600 hover:bg-slate-900"
                  >
                    <action.icon className="mt-0.5 h-4 w-4 shrink-0 text-slate-400 group-hover:text-slate-200" />
                    <span>
                      <span className="block text-sm font-medium text-white">
                        {action.label}
                      </span>
                      <span className="block text-xs text-slate-500">
                        {action.desc}
                      </span>
                    </span>
                  </Link>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="border-slate-800 bg-slate-950/50">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-white">Connections</CardTitle>
              <Link
                to="/connections"
                className="flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200"
              >
                Manage <ArrowRight className="h-3 w-3" />
              </Link>
            </CardHeader>
            <CardContent>
              {!healthy ? (
                <p className="text-sm text-slate-500">
                  Offline - connections appear here when the backend is up.
                </p>
              ) : connectionsQuery.isLoading ? (
                <p className="text-sm text-slate-500">Loading connections...</p>
              ) : connectionList.length === 0 ? (
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm text-slate-500">No connections yet.</p>
                  <Link to="/connection-wizard">
                    <Button
                      size="sm"
                      variant="outline"
                      className="border-slate-700 text-slate-300"
                    >
                      Add one
                    </Button>
                  </Link>
                </div>
              ) : (
                <ul className="space-y-2">
                  {connectionList.slice(0, 5).map((conn, i) => {
                    const name =
                      asString(conn.name) ??
                      asString(conn.connection_name) ??
                      `Connection ${i + 1}`;
                    const dbType =
                      asString(conn.db_type) ?? asString(conn.type) ?? "db";
                    const isActive = activeName !== null && name === activeName;
                    return (
                      <li
                        key={name}
                        className="flex items-center justify-between rounded-md border border-slate-800 bg-slate-900/50 px-3 py-2"
                      >
                        <span className="flex items-center gap-2 text-sm text-white">
                          <Database className="h-3.5 w-3.5 text-slate-500" />
                          {name}
                          <span className="text-xs text-slate-500">
                            {dbType}
                          </span>
                        </span>
                        {isActive && (
                          <Badge className="border-emerald-800 bg-emerald-950 text-xs text-emerald-300">
                            active
                          </Badge>
                        )}
                      </li>
                    );
                  })}
                </ul>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Engines + tool surface */}
      <div className="grid gap-4 lg:grid-cols-7">
        <Card className="border-slate-800 bg-slate-950/50 lg:col-span-4">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-white">Supported engines</CardTitle>
            <Link
              to="/database-types-help"
              className="flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200"
            >
              <FileText className="h-3 w-3" /> Engine guide
            </Link>
          </CardHeader>
          <CardContent>
            {!healthy ? (
              <p className="text-sm text-slate-500">
                Offline - engine list loads from the backend.
              </p>
            ) : supportedQuery.isLoading ? (
              <p className="text-sm text-slate-500">Loading engines...</p>
            ) : (
              <div className="space-y-3">
                {enginesByCategory.map((group) => (
                  <div key={group.category}>
                    <p className="mb-1.5 text-xs font-medium uppercase tracking-wider text-slate-500">
                      {group.category}
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {group.engines.map((engine) => (
                        <Link
                          key={`${group.category}-${engine.type}`}
                          to={`/connection-wizard?type=${engine.type}`}
                          title={`Connect with ${engine.name}`}
                        >
                          <Badge
                            variant="outline"
                            className="border-slate-700 px-2.5 py-1 text-xs text-slate-300 transition-colors hover:border-cyan-600 hover:bg-cyan-950/40 hover:text-cyan-200"
                          >
                            {engine.name}
                          </Badge>
                        </Link>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50 lg:col-span-3">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-white">Tool surface</CardTitle>
            <Link
              to="/mcp-capabilities"
              className="flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200"
            >
              Details <ArrowRight className="h-3 w-3" />
            </Link>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <div className="mb-1 flex justify-between text-xs text-slate-400">
                <span>Portmanteau {portmanteauCount}</span>
                <span>Atomic {atomicCount}</span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-slate-800">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-blue-500 to-violet-500"
                  style={{ width: `${portmanteauPct}%` }}
                />
              </div>
            </div>
            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="rounded-md border border-slate-800 bg-slate-900/50 p-2">
                <div className="text-lg font-bold text-white">
                  {capsQuery.data?.prompts?.count ?? "-"}
                </div>
                <div className="text-xs text-slate-500">Prompts</div>
              </div>
              <div className="rounded-md border border-slate-800 bg-slate-900/50 p-2">
                <div className="text-lg font-bold text-white">
                  {capsQuery.data?.resources?.count ?? "-"}
                </div>
                <div className="text-xs text-slate-500">Resources</div>
              </div>
              <div className="rounded-md border border-slate-800 bg-slate-900/50 p-2">
                <div className="text-lg font-bold text-white">
                  {capsQuery.data?.skills?.count ?? "-"}
                </div>
                <div className="text-xs text-slate-500">Skills</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
