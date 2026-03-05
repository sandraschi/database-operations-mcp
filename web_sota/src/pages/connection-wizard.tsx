import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { callTool } from "@/common/api";
import { getHelpForType } from "@/common/database-types-help";
import { CheckCircle2, Loader2, ArrowRight, ChevronDown, ChevronUp } from "lucide-react";

const DB_TYPES = [
    { value: "sqlite", label: "SQLite (file)" },
    { value: "postgresql", label: "PostgreSQL" },
    { value: "mysql", label: "MySQL" },
    { value: "duckdb", label: "DuckDB" },
    { value: "mongodb", label: "MongoDB" },
    { value: "redis", label: "Redis" },
    { value: "lancedb", label: "LanceDB (vectors)" },
    { value: "chromadb", label: "ChromaDB (vectors)" },
] as const;

function extractData(res: unknown): Record<string, unknown> | null {
    if (res && typeof res === "object" && "data" in res) return (res as { data?: Record<string, unknown> }).data ?? null;
    if (res && typeof res === "object") return res as Record<string, unknown>;
    return null;
}

export function ConnectionWizard() {
    const [step, setStep] = useState(1);
    const [connectionName, setConnectionName] = useState("");
    const [databaseType, setDatabaseType] = useState<string>("sqlite");
    const [config, setConfig] = useState<Record<string, string>>({});
    const [showHelp, setShowHelp] = useState(false);
    const [success, setSuccess] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    const typeHelp = getHelpForType(databaseType);

    const registerMutation = useMutation({
        mutationFn: (args: { name: string; type: string; connection_config: Record<string, unknown> }) =>
            callTool("db_connection", {
                operation: "register",
                connection_name: args.name,
                database_type: args.type,
                connection_config: args.connection_config,
                test_connection: true,
            }),
        onSuccess: (data) => {
            setError(null);
            const d = extractData(data?.result);
            setSuccess(d?.message as string ?? "Connection registered. Set it active on the Connections page.");
        },
        onError: (e: Error) => setError(e.message),
    });

    const configFields: Record<string, { label: string; key: string; placeholder: string }[]> = {
        sqlite: [{ label: "Database path", key: "database", placeholder: "C:/data/mydb.db or ./local.db" }],
        postgresql: [
            { label: "Host", key: "host", placeholder: "localhost" },
            { label: "Port", key: "port", placeholder: "5432" },
            { label: "User", key: "user", placeholder: "postgres" },
            { label: "Password", key: "password", placeholder: "" },
            { label: "Database", key: "database", placeholder: "mydb" },
        ],
        mysql: [
            { label: "Host", key: "host", placeholder: "localhost" },
            { label: "Port", key: "port", placeholder: "3306" },
            { label: "User", key: "user", placeholder: "root" },
            { label: "Password", key: "password", placeholder: "" },
            { label: "Database", key: "database", placeholder: "mydb" },
        ],
        duckdb: [{ label: "Database path", key: "database", placeholder: "C:/data/file.duckdb or :memory:" }],
        mongodb: [
            { label: "Host", key: "host", placeholder: "localhost" },
            { label: "Port", key: "port", placeholder: "27017" },
            { label: "Database", key: "database", placeholder: "myapp" },
        ],
        redis: [
            { label: "Host", key: "host", placeholder: "localhost" },
            { label: "Port", key: "port", placeholder: "6379" },
            { label: "Password", key: "password", placeholder: "(optional)" },
        ],
        lancedb: [
            { label: "URI", key: "uri", placeholder: "./data/lancedb or db://project" },
            { label: "API key", key: "api_key", placeholder: "(cloud only)" },
            { label: "Region", key: "region", placeholder: "us-east-1" },
        ],
        chromadb: [
            { label: "Persist directory", key: "persist_directory", placeholder: "./chroma_data" },
            { label: "Host", key: "host", placeholder: "localhost (server mode)" },
            { label: "Port", key: "port", placeholder: "8000" },
        ],
    };

    const fields = configFields[databaseType as keyof typeof configFields] ?? configFields.sqlite;

    const buildConfig = (): Record<string, unknown> => {
        const out: Record<string, unknown> = {};
        fields.forEach((f) => {
            const v = config[f.key]?.trim();
            if (v !== undefined && v !== "") {
                if (f.key === "port") out[f.key] = Number(v) || 0;
                else out[f.key] = v;
            }
        });
        return out;
    };

    const handleRegister = () => {
        if (!connectionName.trim()) {
            setError("Give the connection a name (e.g. my_db).");
            return;
        }
        const connection_config = buildConfig();
        if (Object.keys(connection_config).length === 0) {
            setError("Fill in at least one connection field.");
            return;
        }
        setError(null);
        setSuccess(null);
        registerMutation.mutate({
            name: connectionName.trim(),
            type: databaseType,
            connection_config,
        });
    };

    const resetWizard = () => {
        setStep(1);
        setConnectionName("");
        setDatabaseType("sqlite");
        setConfig({});
        setSuccess(null);
        setError(null);
    };

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold tracking-tight text-white">Add a connection</h2>
                <p className="text-slate-400">Guided setup: name, type, and connection details</p>
            </div>

            {success ? (
                <Card className="border-emerald-900/50 bg-emerald-950/20">
                    <CardContent className="pt-6">
                        <div className="flex items-start gap-3">
                            <CheckCircle2 className="h-5 w-5 text-emerald-500 shrink-0 mt-0.5" />
                            <div>
                                <p className="text-emerald-200 font-medium">Connection registered</p>
                                <p className="text-slate-400 text-sm mt-1">{success}</p>
                                <Button variant="outline" size="sm" className="mt-4 border-slate-600 text-slate-300" onClick={resetWizard}>
                                    Add another
                                </Button>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            ) : (
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">Step {step}: {step === 1 ? "Name and type" : "Connection details"}</CardTitle>
                        <CardDescription className="text-slate-400">
                            {step === 1
                                ? "Pick a name (e.g. local_db) and the kind of database."
                                : "Fill in the fields for your database. Paths can be absolute or relative."}
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {error && (
                            <div className="rounded-md border border-red-900/50 bg-red-950/20 px-4 py-2 text-sm text-red-400">
                                {error}
                            </div>
                        )}

                        {step === 1 && (
                            <>
                                <div className="grid gap-2">
                                    <Label className="text-slate-300">Connection name</Label>
                                    <input
                                        className="h-9 w-full max-w-xs rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100 placeholder:text-slate-500"
                                        value={connectionName}
                                        onChange={(e) => setConnectionName(e.target.value)}
                                        placeholder="e.g. local_db, prod_backup"
                                    />
                                </div>
                                <div className="grid gap-2">
                                    <Label className="text-slate-300">Database type</Label>
                                    <select
                                        className="h-9 w-full max-w-xs rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100"
                                        value={databaseType}
                                        onChange={(e) => setDatabaseType(e.target.value)}
                                    >
                                        {DB_TYPES.map((t) => (
                                            <option key={t.value} value={t.value}>{t.label}</option>
                                        ))}
                                    </select>
                                </div>
                                {typeHelp && (
                                    <div className="rounded-md border border-slate-700 bg-slate-900/50 overflow-hidden">
                                        <button
                                            type="button"
                                            onClick={() => setShowHelp(!showHelp)}
                                            className="w-full flex items-center justify-between px-4 py-2 text-left text-sm text-slate-300 hover:bg-slate-800/50"
                                        >
                                            <span>Help: {typeHelp.name} — {typeHelp.shortDescription}</span>
                                            {showHelp ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                                        </button>
                                        {showHelp && (
                                            <div className="px-4 pb-4 pt-0 space-y-3 text-sm border-t border-slate-800">
                                                <p className="text-slate-400">{typeHelp.description}</p>
                                                <div>
                                                    <p className="font-medium text-slate-300 mb-1">When to use</p>
                                                    <ul className="list-disc list-inside text-slate-400 space-y-0.5">
                                                        {typeHelp.whenToUse.slice(0, 3).map((u, i) => (
                                                            <li key={i}>{u}</li>
                                                        ))}
                                                    </ul>
                                                </div>
                                                <div>
                                                    <p className="font-medium text-slate-300 mb-1">Required</p>
                                                    <ul className="text-slate-400 space-y-0.5">
                                                        {typeHelp.requiredFields.map((f) => (
                                                            <li key={f.key}><span className="font-mono text-slate-300">{f.label}</span>: {f.description}</li>
                                                        ))}
                                                    </ul>
                                                </div>
                                                {typeHelp.examples.length > 0 && (
                                                    <div>
                                                        <p className="font-medium text-slate-300 mb-1">Examples</p>
                                                        <p className="font-mono text-xs text-slate-400">{typeHelp.examples[0]}</p>
                                                    </div>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                )}
                                <Button className="bg-blue-600 hover:bg-blue-700" onClick={() => setStep(2)}>
                                    Next <ArrowRight className="ml-2 h-4 w-4" />
                                </Button>
                            </>
                        )}

                        {step === 2 && (
                            <>
                                {typeHelp && (
                                    <div className="rounded-md border border-slate-700 bg-slate-900/50 px-4 py-3 text-sm">
                                        <p className="text-slate-300 font-medium mb-1">{typeHelp.name}</p>
                                        <p className="text-slate-400 mb-2">{typeHelp.shortDescription}</p>
                                        <p className="text-slate-500 text-xs">Required: {typeHelp.requiredFields.map((f) => f.label).join(", ")}</p>
                                    </div>
                                )}
                                {fields.map((f) => (
                                    <div key={f.key} className="grid gap-2">
                                        <Label className="text-slate-300">{f.label}</Label>
                                        <input
                                            type={f.key === "password" ? "password" : "text"}
                                            className="h-9 w-full max-w-md rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100 placeholder:text-slate-500"
                                            value={config[f.key] ?? ""}
                                            onChange={(e) => setConfig((prev) => ({ ...prev, [f.key]: e.target.value }))}
                                            placeholder={f.placeholder}
                                        />
                                    </div>
                                ))}
                                <div className="flex gap-2 pt-2">
                                    <Button variant="outline" className="border-slate-700 text-slate-300" onClick={() => setStep(1)}>
                                        Back
                                    </Button>
                                    <Button
                                        className="bg-blue-600 hover:bg-blue-700"
                                        onClick={handleRegister}
                                        disabled={registerMutation.isPending}
                                    >
                                        {registerMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "Test and register"}
                                    </Button>
                                </div>
                            </>
                        )}
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
