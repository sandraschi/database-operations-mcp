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
