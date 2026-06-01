/**
 * REST bridge to backend (MCP gateway).
 * Proxy /api -> backend port 10709 (vite.config.ts).
 */

export interface HealthResponse {
  status: string;
  mcp?: string;
}

export interface McpTool {
  name: string;
  description: string | null;
  inputSchema?: Record<string, unknown>;
}

export interface ToolsResponse {
  tools: McpTool[];
}

export interface CapabilitiesResponse {
  status: string;
  fastmcp?: string;
  tool_surface?: {
    total: number;
    portmanteau_count: number;
    atomic_count: number;
    portmanteau_tools: string[];
    atomic_tools: string[];
  };
  prompts?: {
    available: boolean;
    count: number;
    names: string[];
  };
  resources?: {
    available: boolean;
    count: number;
    uris: string[];
  };
  skills?: {
    available: boolean;
    count: number;
    uris: string[];
  };
  sampling?: {
    available: boolean;
    indicator_tools: string[];
  };
  agentic_workflows?: {
    available: boolean;
    tools: string[];
  };
}

export interface ToolCallRequest {
  name: string;
  arguments: Record<string, unknown>;
}

export interface ToolCallResponse {
  result: unknown;
  isError?: boolean;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  level: string;
  kind: string;
  detail: string;
  meta?: Record<string, unknown>;
}

export interface LogsQueryResponse {
  entries: LogEntry[];
  total: number;
  limit: number;
  offset: number;
  max_entries: number;
  sort: "asc" | "desc";
}

export interface LogStats {
  total: number;
  max_entries: number;
  rotation: string;
  by_level: Record<string, number>;
  by_kind: Record<string, number>;
  oldest: string | null;
  newest: string | null;
}

export interface LogQueryParams {
  limit?: number;
  offset?: number;
  level?: string;
  kind?: string;
  search?: string;
  sort?: "asc" | "desc";
  after_id?: string;
}

const API = "/api";

export async function getHealth(): Promise<HealthResponse> {
  const r = await fetch(`${API}/health`);
  if (!r.ok) throw new Error(`Health check failed: ${r.status}`);
  return r.json();
}

export async function getTools(): Promise<ToolsResponse> {
  const r = await fetch(`${API}/tools`);
  if (!r.ok) throw new Error(`Tools list failed: ${r.status}`);
  return r.json();
}

export async function getCapabilities(): Promise<CapabilitiesResponse> {
  const r = await fetch(`${API}/capabilities`);
  if (!r.ok) throw new Error(`Capabilities failed: ${r.status}`);
  return r.json();
}

export async function callTool(name: string, args: Record<string, unknown>): Promise<ToolCallResponse> {
  const r = await fetch(`${API}/tools/call`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, arguments: args }),
  });
  if (!r.ok) {
    const text = await r.text();
    throw new Error(text || `Tool call failed: ${r.status}`);
  }
  return r.json();
}

function buildLogParams(params: LogQueryParams): string {
  const q = new URLSearchParams();
  if (params.limit != null) q.set("limit", String(params.limit));
  if (params.offset != null) q.set("offset", String(params.offset));
  if (params.level) q.set("level", params.level);
  if (params.kind) q.set("kind", params.kind);
  if (params.search) q.set("search", params.search);
  if (params.sort) q.set("sort", params.sort);
  if (params.after_id) q.set("after_id", params.after_id);
  return q.toString();
}

export async function queryLogs(params: LogQueryParams = {}): Promise<LogsQueryResponse> {
  const qs = buildLogParams(params);
  const r = await fetch(`${API}/logs${qs ? `?${qs}` : ""}`);
  if (!r.ok) throw new Error(`Logs query failed: ${r.status}`);
  return r.json();
}

export async function getLogStats(): Promise<LogStats> {
  const r = await fetch(`${API}/logs/stats`);
  if (!r.ok) throw new Error(`Log stats failed: ${r.status}`);
  return r.json();
}

export async function clearLogs(): Promise<void> {
  const r = await fetch(`${API}/logs`, { method: "DELETE" });
  if (!r.ok) throw new Error(`Clear logs failed: ${r.status}`);
}

export async function downloadLogsExport(
  format: "json" | "csv",
  filters: Omit<LogQueryParams, "limit" | "offset" | "after_id"> = {},
): Promise<void> {
  const q = buildLogParams({ ...filters, limit: undefined, offset: undefined });
  const r = await fetch(`${API}/logs/export?format=${format}${q ? `&${q}` : ""}`);
  if (!r.ok) throw new Error(`Export failed: ${r.status}`);
  const blob = await r.blob();
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `database-operations-mcp-logs.${format}`;
  anchor.click();
  URL.revokeObjectURL(url);
}
