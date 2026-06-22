import { useQuery } from "@tanstack/react-query";
import { Activity, HardDrive, Network, Shield, Wrench } from "lucide-react";
import { getHealth, getTools } from "@/common/api";
import { cn } from "@/common/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function Dashboard() {
  const healthQuery = useQuery({
    queryKey: ["health"],
    queryFn: getHealth,
    refetchInterval: 30_000,
  });
  const toolsQuery = useQuery({
    queryKey: ["tools"],
    queryFn: getTools,
  });

  const healthy = healthQuery.data?.status === "ok";
  const toolCount = toolsQuery.data?.tools?.length ?? 0;
  const loading = healthQuery.isLoading || toolsQuery.isLoading;
  const error = healthQuery.error ?? toolsQuery.error;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">
            Database-operations MCP Dashboard
          </h2>
          <p className="text-slate-400">System overview and status</p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              Service Status
            </CardTitle>
            <Shield
              className={cn(
                "h-4 w-4",
                healthy ? "text-emerald-500" : "text-red-500",
              )}
            />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {loading ? "..." : healthy ? "Online" : "Offline"}
            </div>
            <p className="text-xs text-slate-400">
              {healthQuery.data?.mcp ? "MCP mounted" : "Backend connection"}
            </p>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              Tools
            </CardTitle>
            <Wrench className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {loading ? "..." : toolCount}
            </div>
            <p className="text-xs text-slate-400">MCP tools available</p>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              API Bridge
            </CardTitle>
            <Activity className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {healthy ? "Connected" : "Disconnected"}
            </div>
            <p className="text-xs text-slate-400">FastMCP 3.1 gateway</p>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              Network
            </CardTitle>
            <Network className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {error ? "Error" : healthy ? "Healthy" : "..."}
            </div>
            <p className="text-xs text-slate-400">
              {error ? String(error) : "Backend on :10709"}
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4 border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white">Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[200px] font-mono text-xs p-4 overflow-y-auto border border-slate-800 rounded-md bg-slate-900/50 text-slate-400 space-y-1">
              {loading && (
                <p className="text-blue-400">[system] Checking backend...</p>
              )}
              {healthy && (
                <p className="text-emerald-400">
                  [success] Backend healthy, MCP mounted at /mcp
                </p>
              )}
              {healthy && (
                <p>[network] API /api/tools, /api/tools/call reachable.</p>
              )}
              {error && <p className="text-red-400">[error] {String(error)}</p>}
              {!loading && !error && toolCount > 0 && (
                <p>[tools] {toolCount} tools registered.</p>
              )}
            </div>
          </CardContent>
        </Card>
        <Card className="col-span-3 border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white">Quick stats</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center">
                <HardDrive className="h-4 w-4 text-slate-400 mr-2" />
                <div className="ml-2 space-y-1">
                  <p className="text-sm font-medium leading-none text-white">
                    Backend
                  </p>
                  <p className="text-xs text-slate-400">
                    Single process, MCP + REST
                  </p>
                </div>
              </div>
              <div className="flex items-center">
                <Activity
                  className={cn(
                    "h-4 w-4 mr-2",
                    healthy ? "text-emerald-500" : "text-slate-500",
                  )}
                />
                <div className="ml-2 space-y-1">
                  <p className="text-sm font-medium leading-none text-white">
                    Heartbeat
                  </p>
                  <p className="text-xs text-slate-400">
                    {healthy ? "Nominal" : "No response"}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
