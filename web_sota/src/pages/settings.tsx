import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getCapabilities } from "@/common/api";

export function Settings() {
    const [surfaceMode, setSurfaceMode] = useState("both");
    const [saved, setSaved] = useState<string | null>(null);
    const capsQuery = useQuery({ queryKey: ["capabilities"], queryFn: getCapabilities });

    useEffect(() => {
        const stored = localStorage.getItem("tool-surface-mode");
        if (stored) setSurfaceMode(stored);
    }, []);

    const saveMode = () => {
        localStorage.setItem("tool-surface-mode", surfaceMode);
        setSaved(`Saved mode: ${surfaceMode}`);
        setTimeout(() => setSaved(null), 2000);
    };

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold tracking-tight text-white">Configuration</h2>
                <p className="text-slate-400">Tool surface preferences and MCP feature status</p>
            </div>

            <div className="grid gap-6">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">Tool Surface Mode</CardTitle>
                        <CardDescription className="text-slate-400">Local UI preference for how you want to operate the server surface.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <select
                            className="h-10 w-full rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100"
                            value={surfaceMode}
                            onChange={(e) => setSurfaceMode(e.target.value)}
                        >
                            <option value="both">both (portmanteau + atomic)</option>
                            <option value="portmanteau">portmanteau only</option>
                            <option value="atomic">atomic only</option>
                        </select>
                        <p className="text-xs text-slate-500">
                            This preference is UI-side only; backend env vars control effective registration.
                        </p>
                        <button
                            className="inline-flex h-9 items-center rounded-md border border-slate-700 px-3 text-sm text-slate-300 hover:bg-slate-800"
                            onClick={saveMode}
                        >
                            Save mode preference
                        </button>
                        {saved && <p className="text-sm text-emerald-400">{saved}</p>}
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">FastMCP 3.1 Features</CardTitle>
                        <CardDescription className="text-slate-400">Live capability report from backend.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="flex flex-wrap gap-2">
                            <Badge className="bg-slate-800 text-slate-100 border-0">
                                FastMCP: {capsQuery.data?.fastmcp ?? "unknown"}
                            </Badge>
                            <Badge className="bg-slate-800 text-slate-100 border-0">
                                Prompts: {capsQuery.data?.prompts?.count ?? 0}
                            </Badge>
                            <Badge className="bg-slate-800 text-slate-100 border-0">
                                Skills: {capsQuery.data?.skills?.count ?? 0}
                            </Badge>
                            <Badge className="bg-slate-800 text-slate-100 border-0">
                                Resources: {capsQuery.data?.resources?.count ?? 0}
                            </Badge>
                            <Badge className="bg-slate-800 text-slate-100 border-0">
                                Workflows: {capsQuery.data?.agentic_workflows?.tools.length ?? 0}
                            </Badge>
                        </div>
                        <pre className="max-h-[260px] overflow-auto rounded border border-slate-800 bg-slate-900/40 p-3 text-xs text-slate-300">
                            {JSON.stringify(capsQuery.data ?? { note: "No capability data yet." }, null, 2)}
                        </pre>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
