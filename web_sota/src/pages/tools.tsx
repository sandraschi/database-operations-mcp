import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";
import { getTools, callTool } from "@/common/api";
import { cn } from "@/common/utils";

export function Tools() {
    const queryClient = useQueryClient();
    const [selectedName, setSelectedName] = useState<string | null>(null);
    const [argsJson, setArgsJson] = useState("{}");
    const [callError, setCallError] = useState<string | null>(null);

    const { data, isLoading, error } = useQuery({
        queryKey: ["tools"],
        queryFn: getTools,
    });

    const callMutation = useMutation({
        mutationFn: ({ name, args }: { name: string; args: Record<string, unknown> }) => callTool(name, args),
        onSuccess: () => {
            setCallError(null);
            queryClient.invalidateQueries({ queryKey: ["tools"] });
        },
        onError: (err: Error) => setCallError(err.message),
    });

    const tools = data?.tools ?? [];
    const selected = selectedName ? tools.find((t) => t.name === selectedName) : null;

    const handleCall = () => {
        if (!selectedName) return;
        setCallError(null);
        let args: Record<string, unknown> = {};
        try {
            args = JSON.parse(argsJson || "{}");
        } catch {
            setCallError("Invalid JSON in arguments");
            return;
        }
        callMutation.mutate({ name: selectedName, args });
    };

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold tracking-tight text-white">MCP Tools</h2>
                <p className="text-slate-400">List and call tools via the REST bridge</p>
            </div>

            <div className="grid grid-cols-12 gap-6">
                <Card className="col-span-4 border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">Tools</CardTitle>
                        <CardDescription className="text-slate-400">
                            {tools.length} available
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        {isLoading && <p className="text-slate-400 text-sm">Loading...</p>}
                        {error && <p className="text-red-400 text-sm">{String(error)}</p>}
                        <ScrollArea className="h-[320px] rounded border border-slate-800">
                            <ul className="p-2 space-y-1">
                                {tools.map((t) => (
                                    <li key={t.name}>
                                        <button
                                            type="button"
                                            onClick={() => setSelectedName(t.name)}
                                            className={cn(
                                                "w-full text-left px-3 py-2 rounded text-sm font-mono",
                                                selectedName === t.name
                                                    ? "bg-slate-800 text-white"
                                                    : "text-slate-400 hover:bg-slate-800/50"
                                            )}
                                        >
                                            {t.name}
                                        </button>
                                    </li>
                                ))}
                            </ul>
                        </ScrollArea>
                    </CardContent>
                </Card>

                <Card className="col-span-8 border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">
                            {selected ? selected.name : "Select a tool"}
                        </CardTitle>
                        {selected?.description && (
                            <CardDescription className="text-slate-400 whitespace-pre-wrap">
                                {selected.description}
                            </CardDescription>
                        )}
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {selected && (
                            <>
                                <div className="grid gap-2">
                                    <Label className="text-slate-300">Arguments (JSON)</Label>
                                    <textarea
                                        className="min-h-[120px] w-full rounded-md border border-slate-800 bg-slate-900 p-3 font-mono text-sm text-slate-100 placeholder:text-slate-500"
                                        value={argsJson}
                                        onChange={(e) => setArgsJson(e.target.value)}
                                        placeholder='{"key": "value"}'
                                    />
                                </div>
                                {callError && (
                                    <p className="text-red-400 text-sm">{callError}</p>
                                )}
                                {callMutation.data && (
                                    <div className="rounded border border-slate-800 bg-slate-900/50 p-3">
                                        <p className="text-xs text-slate-500 mb-1">Result</p>
                                        <pre className="text-sm text-slate-300 whitespace-pre-wrap break-all">
                                            {JSON.stringify(callMutation.data.result, null, 2)}
                                        </pre>
                                        {callMutation.data.isError && (
                                            <p className="text-amber-400 text-xs mt-1">Tool returned error</p>
                                        )}
                                    </div>
                                )}
                                <Button
                                    onClick={handleCall}
                                    disabled={callMutation.isPending}
                                    className="bg-blue-600 hover:bg-blue-700"
                                >
                                    {callMutation.isPending ? "Calling..." : "Call tool"}
                                </Button>
                            </>
                        )}
                        {!selected && !isLoading && (
                            <p className="text-slate-500 text-sm">Select a tool from the list to call it.</p>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
