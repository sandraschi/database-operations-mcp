import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";
import { callTool } from "@/common/api";
import { cn } from "@/common/utils";
import { Table2, Database, FileText } from "lucide-react";

function extractData(res: unknown): Record<string, unknown> | null {
    if (res && typeof res === "object" && "data" in res) return (res as { data?: Record<string, unknown> }).data ?? null;
    if (res && typeof res === "object") return res as Record<string, unknown>;
    return null;
}

export function Schema() {
    const [connectionName, setConnectionName] = useState("");
    const [databases, setDatabases] = useState<string[]>([]);
    const [tables, setTables] = useState<string[]>([]);
    const [describe, setDescribe] = useState<Record<string, unknown> | null>(null);
    const [selectedDb, setSelectedDb] = useState<string | null>(null);
    const [selectedTable, setSelectedTable] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    const listDbMutation = useMutation({
        mutationFn: (conn: string) => callTool("db_schema", { operation: "list_databases", connection_name: conn }),
        onSuccess: (data, conn) => {
            setError(null);
            const d = extractData(data?.result);
            const list = (d?.databases as string[]) ?? (d?.items as string[]) ?? [];
            setDatabases(Array.isArray(list) ? list : []);
            setTables([]);
            setDescribe(null);
            setSelectedDb(null);
            setSelectedTable(null);
        },
        onError: (e: Error) => setError(e.message),
    });

    const listTablesMutation = useMutation({
        mutationFn: ({ conn, db }: { conn: string; db: string | null }) =>
            callTool("db_schema", {
                operation: "list_tables",
                connection_name: conn,
                database_name: db ?? undefined,
            }),
        onSuccess: (data) => {
            setError(null);
            const d = extractData(data?.result);
            const list = (d?.tables as string[]) ?? (d?.items as string[]) ?? [];
            setTables(Array.isArray(list) ? list : []);
            setDescribe(null);
            setSelectedTable(null);
        },
        onError: (e: Error) => setError(e.message),
    });

    const describeMutation = useMutation({
        mutationFn: ({ conn, table }: { conn: string; table: string }) =>
            callTool("db_schema", {
                operation: "describe_table",
                connection_name: conn,
                table_name: table,
            }),
        onSuccess: (data) => {
            setError(null);
            setDescribe(extractData(data?.result) ?? null);
        },
        onError: (e: Error) => setError(e.message),
    });

    const loadActiveAndList = () => {
        if (!connectionName.trim()) {
            setError("Enter a connection name (or use Connections page to set active).");
            return;
        }
        setError(null);
        listDbMutation.mutate(connectionName.trim());
    };

    const onSelectDb = (db: string) => {
        setSelectedDb(db);
        listTablesMutation.mutate({ conn: connectionName.trim(), db });
    };

    const onSelectTable = (table: string) => {
        setSelectedTable(table);
        describeMutation.mutate({ conn: connectionName.trim(), table });
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Schema</h2>
                    <p className="text-slate-400">List databases, tables, and inspect columns</p>
                </div>
            </div>

            <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader>
                    <CardTitle className="text-white">Connection</CardTitle>
                    <CardDescription className="text-slate-400">
                        Use the same name as in Connections (active connection name).
                    </CardDescription>
                </CardHeader>
                <CardContent className="flex flex-wrap items-end gap-4">
                    <div className="grid gap-2">
                        <Label className="text-slate-300">Connection name</Label>
                        <input
                            className="h-9 w-64 rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100 placeholder:text-slate-500"
                            value={connectionName}
                            onChange={(e) => setConnectionName(e.target.value)}
                            placeholder="e.g. local_sqlite"
                        />
                    </div>
                    <Button
                        className="bg-blue-600 hover:bg-blue-700"
                        onClick={loadActiveAndList}
                        disabled={listDbMutation.isPending || !connectionName.trim()}
                    >
                        {listDbMutation.isPending ? "Loading..." : "Load databases"}
                    </Button>
                </CardContent>
            </Card>

            {error && (
                <div className="rounded-md border border-red-900/50 bg-red-950/20 px-4 py-2 text-sm text-red-400">
                    {error}
                </div>
            )}

            <div className="grid gap-6 md:grid-cols-3">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            <Database className="h-4 w-4 text-blue-500" />
                            Databases
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ScrollArea className="h-[240px] rounded border border-slate-800">
                            <ul className="p-2 space-y-1">
                                {databases.map((db) => (
                                    <li key={db}>
                                        <button
                                            type="button"
                                            onClick={() => onSelectDb(db)}
                                            className={cn(
                                                "w-full text-left px-3 py-2 rounded text-sm font-mono",
                                                selectedDb === db ? "bg-slate-800 text-white" : "text-slate-400 hover:bg-slate-800/50"
                                            )}
                                        >
                                            {db}
                                        </button>
                                    </li>
                                ))}
                            </ul>
                        </ScrollArea>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            <Table2 className="h-4 w-4 text-emerald-500" />
                            Tables
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ScrollArea className="h-[240px] rounded border border-slate-800">
                            <ul className="p-2 space-y-1">
                                {tables.map((t) => (
                                    <li key={t}>
                                        <button
                                            type="button"
                                            onClick={() => onSelectTable(t)}
                                            className={cn(
                                                "w-full text-left px-3 py-2 rounded text-sm font-mono",
                                                selectedTable === t ? "bg-slate-800 text-white" : "text-slate-400 hover:bg-slate-800/50"
                                            )}
                                        >
                                            {t}
                                        </button>
                                    </li>
                                ))}
                            </ul>
                        </ScrollArea>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            <FileText className="h-4 w-4 text-amber-500" />
                            Table schema
                        </CardTitle>
                        <CardDescription className="text-slate-400">
                            {selectedTable ? `Columns and metadata for ${selectedTable}` : "Select a table"}
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <ScrollArea className="h-[240px] rounded border border-slate-800">
                            {describe ? (
                                <pre className="p-3 text-xs text-slate-300 whitespace-pre-wrap break-all">
                                    {JSON.stringify(describe, null, 2)}
                                </pre>
                            ) : (
                                <p className="p-3 text-slate-500 text-sm">Select a table to describe.</p>
                            )}
                        </ScrollArea>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
