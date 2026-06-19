import { useState, useRef } from "react";
import { useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { callTool } from "@/common/api";
import { FileDown, FileUp, Download, Upload } from "lucide-react";

function extractData(res: unknown): Record<string, unknown> | null {
    if (res && typeof res === "object" && "data" in res) return (res as { data?: Record<string, unknown> }).data ?? null;
    if (res && typeof res === "object") return res as Record<string, unknown>;
    return null;
}

function downloadBlob(content: string, filename: string, mime: string) {
    const blob = new Blob([content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

function rowsToCSV(rows: Record<string, unknown>[], columns: string[]): string {
    const header = columns.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(",");
    const lines = rows.map((r) =>
        columns.map((c) => {
            const v = (r as Record<string, unknown>)[c];
            return `"${String(v ?? "").replace(/"/g, '""')}"`;
        }).join(",")
    );
    return [header, ...lines].join("\r\n");
}

export function ExportImport() {
    const [connectionName, setConnectionName] = useState("");
    const [exportQuery, setExportQuery] = useState("SELECT * FROM sqlite_master LIMIT 10");
    const [exportResult, setExportResult] = useState<{ rows?: Record<string, unknown>[]; columns?: string[] } | null>(null);
    const [importTable, setImportTable] = useState("");
    const [importJson, setImportJson] = useState("");
    const [importFile, setImportFile] = useState<File | null>(null);
    const [message, setMessage] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const exportMutation = useMutation({
        mutationFn: ({ conn, query }: { conn: string; query: string }) =>
            callTool("db_operations", {
                operation: "execute_query",
                connection_name: conn,
                query,
                limit: 10_000,
            }),
        onSuccess: (data) => {
            setError(null);
            const d = extractData(data?.result);
            const rows = (d?.rows as Record<string, unknown>[]) ?? (d?.result as Record<string, unknown>[]) ?? [];
            const columns = (d?.columns as string[]) ?? (rows.length > 0 ? Object.keys(rows[0] as object) : []);
            setExportResult({ rows: Array.isArray(rows) ? rows : [], columns });
        },
        onError: (e: Error) => setError(e.message),
    });

    const importMutation = useMutation({
        mutationFn: ({ conn, table, data }: { conn: string; table: string; data: Record<string, unknown>[] }) =>
            callTool("db_operations", {
                operation: "batch_insert",
                connection_name: conn,
                table_name: table,
                data,
                batch_size: 500,
            }),
        onSuccess: (data) => {
            setError(null);
            const d = extractData(data?.result);
            const total = (d?.total_inserted as number) ?? (d?.rows_affected as number);
            setMessage(`Inserted ${total ?? "?"} row(s).`);
        },
        onError: (e: Error) => setError(e.message),
    });

    const runExport = () => {
        if (!connectionName.trim() || !exportQuery.trim()) {
            setError("Connection and query required.");
            return;
        }
        setExportResult(null);
        exportMutation.mutate({ conn: connectionName.trim(), query: exportQuery.trim() });
    };

    const downloadAsJson = () => {
        if (!exportResult?.rows) return;
        downloadBlob(JSON.stringify(exportResult.rows, null, 2), "export.json", "application/json");
    };

    const downloadAsCsv = () => {
        if (!exportResult?.rows?.length || !exportResult?.columns?.length) return;
        downloadBlob(rowsToCSV(exportResult.rows, exportResult.columns), "export.csv", "text/csv;charset=utf-8");
    };

    const parseImportData = (): Record<string, unknown>[] | null => {
        if (importJson.trim()) {
            try {
                const parsed = JSON.parse(importJson) as unknown;
                if (Array.isArray(parsed)) return parsed as Record<string, unknown>[];
                if (parsed && typeof parsed === "object" && "rows" in parsed) return (parsed as { rows: Record<string, unknown>[] }).rows;
                setError("JSON must be an array of objects or { rows: [...] }.");
                return null;
            } catch {
                setError("Invalid JSON.");
                return null;
            }
        }
        if (importFile) {
            return null;
        }
        setError("Paste JSON array or choose a CSV file.");
        return null;
    };

    const runImportFromJson = () => {
        if (!connectionName.trim() || !importTable.trim()) {
            setError("Connection and table name required.");
            return;
        }
        const data = parseImportData();
        if (!data?.length) return;
        setMessage(null);
        importMutation.mutate({ conn: connectionName.trim(), table: importTable.trim(), data });
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const f = e.target.files?.[0];
        setImportFile(f ?? null);
    };

    const runImportFromFile = async () => {
        if (!importFile || !connectionName.trim() || !importTable.trim()) {
            setError("Connection, table name, and file required.");
            return;
        }
        setMessage(null);
        const text = await importFile.text();
        const isJson = importFile.name.toLowerCase().endsWith(".json");
        let data: Record<string, unknown>[];
        if (isJson) {
            try {
                const parsed = JSON.parse(text) as unknown;
                data = Array.isArray(parsed) ? (parsed as Record<string, unknown>[]) : (parsed as { rows?: Record<string, unknown>[] }).rows ?? [];
            } catch {
                setError("Invalid JSON file.");
                return;
            }
        } else {
            const lines = text.split(/\r?\n/).filter((l) => l.trim());
            if (lines.length < 2) {
                setError("CSV must have header and at least one row.");
                return;
            }
            const headers = lines[0].split(",").map((h) => h.replace(/^"|"$/g, "").trim());
            data = lines.slice(1).map((line) => {
                const values = line.split(",").map((v) => v.replace(/^"|"$/g, "").trim());
                const row: Record<string, unknown> = {};
                headers.forEach((h, i) => { row[h] = values[i] ?? ""; });
                return row;
            });
        }
        if (!data.length) {
            setError("No rows to insert.");
            return;
        }
        importMutation.mutate({ conn: connectionName.trim(), table: importTable.trim(), data });
    };

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold tracking-tight text-white">Export / Import</h2>
                <p className="text-slate-400">Export query results (JSON/CSV download) and import data via batch_insert</p>
            </div>

            <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader>
                    <CardTitle className="text-white">Connection</CardTitle>
                    <CardDescription className="text-slate-400">Used for both export and import.</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="grid gap-2 max-w-xs">
                        <Label className="text-slate-300">Connection name</Label>
                        <input
                            className="h-9 rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100 placeholder:text-slate-500"
                            value={connectionName}
                            onChange={(e) => setConnectionName(e.target.value)}
                            placeholder="e.g. local_sqlite"
                        />
                    </div>
                </CardContent>
            </Card>

            {error && (
                <div className="rounded-md border border-red-900/50 bg-red-950/20 px-4 py-2 text-sm text-red-400">
                    {error}
                </div>
            )}
            {message && (
                <div className="rounded-md border border-emerald-900/50 bg-emerald-950/20 px-4 py-2 text-sm text-emerald-400">
                    {message}
                </div>
            )}

            <div className="grid gap-6 lg:grid-cols-2">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            <FileDown className="h-4 w-4 text-blue-500" />
                            Export
                        </CardTitle>
                        <CardDescription className="text-slate-400">
                            Run a query (max 10k rows), then download as JSON or CSV. Uses db_operations execute_query.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid gap-2">
                            <Label className="text-slate-300">Query (SELECT)</Label>
                            <textarea
                                className="min-h-[80px] w-full rounded-md border border-slate-800 bg-slate-900 p-3 font-mono text-sm text-slate-100 placeholder:text-slate-500"
                                value={exportQuery}
                                onChange={(e) => setExportQuery(e.target.value)}
                                placeholder="SELECT * FROM ..."
                            />
                        </div>
                        <Button
                            className="bg-blue-600 hover:bg-blue-700"
                            onClick={runExport}
                            disabled={exportMutation.isPending || !connectionName.trim() || !exportQuery.trim()}
                        >
                            {exportMutation.isPending ? "Running..." : "Run query"}
                        </Button>
                        {exportResult && (
                            <div className="space-y-2">
                                <p className="text-sm text-slate-400">{exportResult.rows?.length ?? 0} rows</p>
                                <div className="flex gap-2">
                                    <Button variant="outline" size="sm" className="border-slate-700 text-slate-300" onClick={downloadAsJson}>
                                        <Download className="mr-2 h-3 w-3" /> JSON
                                    </Button>
                                    <Button variant="outline" size="sm" className="border-slate-700 text-slate-300" onClick={downloadAsCsv}>
                                        <Download className="mr-2 h-3 w-3" /> CSV
                                    </Button>
                                </div>
                            </div>
                        )}
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            <FileUp className="h-4 w-4 text-emerald-500" />
                            Import
                        </CardTitle>
                        <CardDescription className="text-slate-400">
                            Paste JSON array of objects or upload JSON/CSV; inserts via db_operations batch_insert.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid gap-2">
                            <Label className="text-slate-300">Target table</Label>
                            <input
                                className="h-9 w-full rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100 placeholder:text-slate-500"
                                value={importTable}
                                onChange={(e) => setImportTable(e.target.value)}
                                placeholder="e.g. my_table"
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label className="text-slate-300">JSON array (optional if using file)</Label>
                            <textarea
                                className="min-h-[100px] w-full rounded-md border border-slate-800 bg-slate-900 p-3 font-mono text-sm text-slate-100 placeholder:text-slate-500"
                                value={importJson}
                                onChange={(e) => setImportJson(e.target.value)}
                                placeholder='[{"col1": "a", "col2": 1}, ...]'
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label className="text-slate-300">Or upload file (JSON or CSV)</Label>
                            <input
                                ref={fileInputRef}
                                type="file"
                                accept=".json,.csv,application/json,text/csv"
                                className="text-sm text-slate-400 file:mr-2 file:rounded file:border-0 file:bg-slate-800 file:px-3 file:py-1 file:text-slate-200"
                                onChange={handleFileChange}
                            />
                            {importFile && <span className="text-xs text-slate-500">{importFile.name}</span>}
                        </div>
                        <div className="flex gap-2">
                            <Button
                                className="bg-emerald-600 hover:bg-emerald-700"
                                onClick={runImportFromJson}
                                disabled={importMutation.isPending || !connectionName.trim() || !importTable.trim() || !importJson.trim()}
                            >
                                {importMutation.isPending ? "Importing..." : "Import from JSON"}
                            </Button>
                            <Button
                                variant="outline"
                                className="border-slate-700 text-slate-300 hover:bg-slate-800"
                                onClick={runImportFromFile}
                                disabled={importMutation.isPending || !connectionName.trim() || !importTable.trim() || !importFile}
                            >
                                <Upload className="mr-2 h-3 w-3" /> From file
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
