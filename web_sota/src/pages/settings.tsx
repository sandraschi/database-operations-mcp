import { useCallback, useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getCapabilities } from "@/common/api";
import { API_BASE } from "@/lib/api";

function LLMSettings() {
    const [providers, setProviders] = useState<Record<string, {name:string}[]>>({});
    const [selectedProvider, setSelectedProvider] = useState("ollama");
    const [selectedModel, setSelectedModel] = useState("");
    const [status, setStatus] = useState<"loading"|"ready"|"error">("loading");

    useEffect(() => {
        fetch(API_BASE + "/api/llm/providers")
            .then(r => r.json())
            .then(d => {
                setProviders(d);
                const savedP = localStorage.getItem("llm_provider") || "ollama";
                const savedM = localStorage.getItem("llm_model") || "";
                setSelectedProvider(savedP);
                const models = d[savedP === "ollama" ? "ollama" : "lm_studio"] || [];
                setSelectedModel(savedM && models.some((m:{name:string}) => m.name === savedM) ? savedM : (models[0]?.name || ""));
                setStatus(models.length > 0 ? "ready" : "error");
            })
            .catch(() => {
                setProviders({ ollama: [{name:"llama3.2:3b"}] });
                setSelectedModel(localStorage.getItem("llm_model") || "llama3.2:3b");
                setStatus("ready");
            });
    }, []);

    const saveConfig = useCallback((provider: string, model: string) => {
        localStorage.setItem("llm_provider", provider);
        localStorage.setItem("llm_model", model);
    }, []);

    const handleProviderChange = (p: string) => {
        setSelectedProvider(p);
        const models = providers[p === "ollama" ? "ollama" : "lm_studio"] || [];
        const first = models[0]?.name || "";
        setSelectedModel(first);
        saveConfig(p, first);
    };

    const handleModelChange = (m: string) => {
        setSelectedModel(m);
        saveConfig(selectedProvider, m);
    };

    const currentModels = providers[selectedProvider === "ollama" ? "ollama" : "lm_studio"] || [];

    return (
        <Card className="border-slate-800 bg-slate-950/50">
            <CardHeader>
                <CardTitle className="text-white">Local LLM</CardTitle>
                <CardDescription className="text-slate-400">
                    Configure which LLM backend the AI tools use (agentic workflow, NL control, log analysis).
                    {status === "ready" ? (
                        <span className="ml-2 inline-flex items-center gap-1 text-emerald-400">
                            <span className="h-2 w-2 rounded-full bg-emerald-400" /> reachable
                        </span>
                    ) : (
                        <span className="ml-2 inline-flex items-center gap-1 text-amber-400">
                            <span className="h-2 w-2 rounded-full bg-amber-400" /> probing...
                        </span>
                    )}
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                <div>
                    <label className="text-xs text-slate-400 mb-1 block">Provider</label>
                    <select className="h-10 w-full rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100"
                        value={selectedProvider} onChange={(e) => handleProviderChange(e.target.value)}>
                        <option value="ollama">Ollama</option>
                        <option value="lm_studio">LM Studio</option>
                    </select>
                </div>
                <div>
                    <label className="text-xs text-slate-400 mb-1 block">Model</label>
                    <select className="h-10 w-full rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100"
                        value={selectedModel} onChange={(e) => handleModelChange(e.target.value)}>
                        {currentModels.map((m) => (
                            <option key={m.name} value={m.name}>{m.name}</option>
                        ))}
                    </select>
                </div>
                <p className="text-xs text-slate-500">
                    Saved to browser storage. Used by the LLM Chat page and AI tools (agentic workflows, natural language control, log analysis).
                </p>
            </CardContent>
        </Card>
    );
}

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
                <p className="text-slate-400">Tool surface preferences, LLM provider, and MCP feature status</p>
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

                <LLMSettings />

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
