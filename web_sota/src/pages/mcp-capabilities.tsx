import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getCapabilities } from "@/common/api";

export function McpCapabilities() {
  const capsQuery = useQuery({ queryKey: ["capabilities"], queryFn: getCapabilities });
  const data = capsQuery.data;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">MCP Capabilities</h2>
        <p className="text-slate-400">FastMCP 3.1 feature visibility for prompts, resources, skills, and workflows.</p>
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white">Feature Flags</CardTitle>
          <CardDescription className="text-slate-400">Reported by backend capability introspection.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          <Badge className="bg-slate-800 text-slate-100 border-0">FastMCP: {data?.fastmcp ?? "unknown"}</Badge>
          <Badge className="bg-slate-800 text-slate-100 border-0">
            Sampling: {data?.sampling?.available ? "available" : "not detected"}
          </Badge>
          <Badge className="bg-slate-800 text-slate-100 border-0">
            Workflows: {data?.agentic_workflows?.available ? "available" : "not detected"}
          </Badge>
          <Badge className="bg-slate-800 text-slate-100 border-0">
            Skills: {data?.skills?.available ? "available" : "not detected"}
          </Badge>
          <Badge className="bg-slate-800 text-slate-100 border-0">
            Prompts: {data?.prompts?.available ? "available" : "not detected"}
          </Badge>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white">Sampling & Agentic</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="max-h-[320px] overflow-auto rounded border border-slate-800 bg-slate-900/40 p-3 text-xs text-slate-300">
              {JSON.stringify(
                {
                  sampling: data?.sampling,
                  agentic_workflows: data?.agentic_workflows,
                },
                null,
                2,
              )}
            </pre>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white">Prompts / Resources / Skills</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="max-h-[320px] overflow-auto rounded border border-slate-800 bg-slate-900/40 p-3 text-xs text-slate-300">
              {JSON.stringify(
                {
                  prompts: data?.prompts,
                  resources: data?.resources,
                  skills: data?.skills,
                },
                null,
                2,
              )}
            </pre>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
