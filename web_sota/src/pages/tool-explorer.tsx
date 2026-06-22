import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { getCapabilities, getTools } from "@/common/api";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

function getFamily(toolName: string): string {
  if (toolName.startsWith("db_")) return "database";
  if (toolName.startsWith("firefox_")) return "firefox";
  if (
    toolName.startsWith("chrome_") ||
    toolName.startsWith("edge_") ||
    toolName.startsWith("brave_")
  )
    return "chromium";
  if (toolName.includes("bookmark")) return "bookmarks";
  if (
    toolName.includes("media") ||
    toolName.includes("plex") ||
    toolName.includes("calibre")
  )
    return "media";
  if (toolName.includes("system") || toolName.includes("registry"))
    return "system";
  return "other";
}

export function ToolExplorer() {
  const [q, setQ] = useState("");
  const toolsQuery = useQuery({ queryKey: ["tools"], queryFn: getTools });
  const capsQuery = useQuery({
    queryKey: ["capabilities"],
    queryFn: getCapabilities,
  });

  const tools = toolsQuery.data?.tools ?? [];
  const qLower = q.trim().toLowerCase();

  const filtered = useMemo(
    () =>
      tools.filter((t) => {
        if (!qLower) return true;
        return (
          t.name.toLowerCase().includes(qLower) ||
          (t.description ?? "").toLowerCase().includes(qLower)
        );
      }),
    [tools, qLower],
  );

  const grouped = useMemo(() => {
    const map = new Map<string, typeof filtered>();
    for (const tool of filtered) {
      const fam = getFamily(tool.name);
      const arr = map.get(fam) ?? [];
      arr.push(tool);
      map.set(fam, arr);
    }
    return [...map.entries()].sort((a, b) => a[0].localeCompare(b[0]));
  }, [filtered]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">
          Tool Explorer
        </h2>
        <p className="text-slate-400">
          Browse MCP tools by domain, capability, and shape.
        </p>
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white">Surface Overview</CardTitle>
          <CardDescription className="text-slate-400">
            {capsQuery.data?.tool_surface?.total ?? tools.length} tools exposed
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          <Badge className="bg-slate-800 text-slate-200 border-0">
            Portmanteau: {capsQuery.data?.tool_surface?.portmanteau_count ?? 0}
          </Badge>
          <Badge className="bg-slate-800 text-slate-200 border-0">
            Atomic: {capsQuery.data?.tool_surface?.atomic_count ?? 0}
          </Badge>
          <Badge className="bg-slate-800 text-slate-200 border-0">
            Sampling: {capsQuery.data?.sampling?.available ? "yes" : "no"}
          </Badge>
          <Badge className="bg-slate-800 text-slate-200 border-0">
            Workflows: {capsQuery.data?.agentic_workflows?.tools.length ?? 0}
          </Badge>
        </CardContent>
      </Card>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white">Find Tools</CardTitle>
        </CardHeader>
        <CardContent>
          <input
            className="h-10 w-full rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100 placeholder:text-slate-500"
            placeholder="Search by tool name or description"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </CardContent>
      </Card>

      {grouped.map(([family, familyTools]) => (
        <Card key={family} className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white capitalize">{family}</CardTitle>
            <CardDescription className="text-slate-400">
              {familyTools.length} tool(s)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {familyTools.map((tool) => (
              <div
                key={tool.name}
                className="rounded border border-slate-800 bg-slate-900/40 p-3"
              >
                <p className="font-mono text-sm text-slate-100">{tool.name}</p>
                <p className="mt-1 text-sm text-slate-400 whitespace-pre-wrap">
                  {tool.description || "No description"}
                </p>
              </div>
            ))}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
