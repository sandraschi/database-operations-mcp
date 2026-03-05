import { useState } from 'react';
import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
    Database,
    Search,
    Table,
    FileCode,
    RefreshCw,
    AlertCircle,
    HardDrive,
    Info,
    ChevronLeft,
    ChevronRight,
} from "lucide-react";
import { cn } from "@/common/utils";

interface TableInfo {
    table_name: string;
    table_type: string;
    row_count: number;
}

export default function DatabaseBrowser() {
    const [dbPath, setDbPath] = useState('');
    const [tables, setTables] = useState<TableInfo[]>([]);
    const [selectedTable, setSelectedTable] = useState<string | null>(null);
    const [tableData, setTableData] = useState<any[]>([]);
    const [columns, setColumns] = useState<string[]>([]);
    const [schema, setSchema] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState('');

    const inspectDb = async () => {
        if (!dbPath) return;
        setLoading(true);
        setSelectedTable(null);
        setTableData([]);
        setError(null);
        try {
            // @ts-ignore - Tool call to mcp-server
            const result = await window.mcp.callTool('database-operations-mcp', 'sqlite_inspect_db', { db_path: dbPath });

            if (result.success) {
                setTables(result.tables);
            } else {
                setError(result.error || 'Failed to open database');
            }
        } catch (e) {
            setError('Failed to communicate with DB engine. Ensure MCP server is running.');
        } finally {
            setLoading(false);
        }
    };

    const loadTable = async (tableName: string) => {
        setSelectedTable(tableName);
        setLoading(true);
        try {
            // @ts-ignore
            const dataResult = await window.mcp.callTool('database-operations-mcp', 'sqlite_get_table_data', {
                db_path: dbPath,
                table_name: tableName,
                limit: 100
            });

            if (dataResult.success) {
                setColumns(dataResult.columns);
                setTableData(dataResult.data);
            } else {
                setError(dataResult.error || 'Failed to load table data');
            }

            // @ts-ignore
            const schemaResult = await window.mcp.callTool('database-operations-mcp', 'sqlite_get_table_schema', {
                db_path: dbPath,
                table_name: tableName
            });

            if (schemaResult.success) {
                setSchema(schemaResult.create_sql);
            }
        } catch (e) {
            setError(`Failed to load table ${tableName}`);
        } finally {
            setLoading(false);
        }
    };

    const filteredTables = tables.filter(t =>
        t.table_name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="flex flex-col gap-6 p-6 max-h-screen overflow-hidden">
            <div className="flex items-center justify-between shrink-0">
                <div>
                    <h1 className="text-3xl font-bold text-slate-100 tracking-tight flex items-center gap-3">
                        <HardDrive className="h-8 w-8 text-blue-500" />
                        Filesystem DB Browser
                    </h1>
                    <p className="text-slate-400 mt-1 italic">Industrial-grade arbitrary SQLite explorer</p>
                </div>
            </div>

            <Card className="border-slate-800 bg-slate-900/50 backdrop-blur-xl shrink-0">
                <CardContent className="p-4">
                    <div className="flex gap-4">
                        <div className="relative flex-1">
                            <Database className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                            <Input
                                placeholder="Enter absolute path to SQLite file (e.g., C:/path/to/data.db)"
                                value={dbPath}
                                onChange={(e) => setDbPath(e.target.value)}
                                className="pl-9 bg-slate-950/50 border-slate-800"
                            />
                        </div>
                        <Button
                            onClick={inspectDb}
                            disabled={loading || !dbPath}
                            className="bg-blue-600 hover:bg-blue-500 text-white min-w-[120px]"
                        >
                            {loading ? <RefreshCw className="h-4 w-4 animate-spin mr-2" /> : <Eye className="h-4 w-4 mr-2" />}
                            Inspect DB
                        </Button>
                    </div>
                    {error && (
                        <div className="mt-3 flex items-center gap-2 text-red-400 text-sm bg-red-400/10 p-2 rounded border border-red-400/20">
                            <AlertCircle className="h-4 w-4 shrink-0" />
                            {error}
                        </div>
                    )}
                </CardContent>
            </Card>

            <div className="grid grid-cols-12 gap-6 min-h-0 flex-1">
                {/* Tables List */}
                <Card className="col-span-3 border-slate-800 bg-slate-900/50 flex flex-col min-h-0">
                    <CardHeader className="p-4 border-b border-slate-800 shrink-0">
                        <div className="flex items-center justify-between mb-3">
                            <h3 className="font-semibold text-slate-100 flex items-center gap-2">
                                <Table className="h-4 w-4 text-blue-400" />
                                Tables
                            </h3>
                            <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 uppercase tracking-wider font-bold">
                                {tables.length} Found
                            </span>
                        </div>
                        <div className="relative">
                            <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-500" />
                            <Input
                                placeholder="Filter tables..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="pl-8 h-8 text-xs bg-slate-950/30 border-slate-800"
                            />
                        </div>
                    </CardHeader>
                    <CardContent className="p-0 overflow-y-auto flex-1">
                        {tables.length === 0 ? (
                            <div className="p-8 text-center text-slate-600 text-sm italic">
                                No database loaded
                            </div>
                        ) : (
                            <div className="divide-y divide-slate-800/50">
                                {filteredTables.map((table) => (
                                    <button
                                        key={table.table_name}
                                        onClick={() => loadTable(table.table_name)}
                                        className={cn(
                                            "w-full text-left px-4 py-3 text-sm transition-colors hover:bg-slate-800/50 group flex items-center justify-between",
                                            selectedTable === table.table_name ? "bg-blue-500/10 border-l-2 border-blue-500 text-blue-400" : "text-slate-400"
                                        )}
                                    >
                                        <div className="truncate">
                                            <div className="font-medium truncate group-hover:text-slate-200">{table.table_name}</div>
                                            <div className="text-[10px] opacity-50 flex items-center gap-1 mt-0.5">
                                                <Info className="h-2.5 w-2.5" />
                                                {table.row_count.toLocaleString()} rows
                                            </div>
                                        </div>
                                    </button>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Data View */}
                <Card className="col-span-9 border-slate-800 bg-slate-900/50 flex flex-col min-h-0">
                    <CardHeader className="p-4 border-b border-slate-800 shrink-0 flex flex-row items-center justify-between">
                        <div>
                            <CardTitle className="text-lg text-slate-100 flex items-center gap-2">
                                {selectedTable ? (
                                    <>
                                        <Table className="h-4 w-4 text-blue-400" />
                                        {selectedTable}
                                    </>
                                ) : 'Data Explorer'}
                            </CardTitle>
                        </div>
                        {selectedTable && (
                            <div className="flex gap-2">
                                <Button variant="ghost" size="sm" className="h-8 text-xs text-slate-400 hover:text-white">
                                    <FileCode className="h-3.5 w-3.5 mr-1" />
                                    View Schema
                                </Button>
                            </div>
                        )}
                    </CardHeader>
                    <CardContent className="p-0 flex-1 flex flex-col overflow-hidden">
                        {!selectedTable ? (
                            <div className="flex-1 flex flex-col items-center justify-center text-slate-600 gap-4">
                                <Search className="h-12 w-12 opacity-10" />
                                <p>Select a table to browse its contents</p>
                            </div>
                        ) : loading ? (
                            <div className="flex-1 flex items-center justify-center text-blue-500 gap-2">
                                <RefreshCw className="h-6 w-6 animate-spin" />
                                Thinking...
                            </div>
                        ) : (
                            <>
                                <div className="flex-1 overflow-auto">
                                    <table className="w-full text-left text-xs border-collapse">
                                        <thead className="sticky top-0 z-10 bg-slate-900 shadow-sm border-b border-slate-700">
                                            <tr>
                                                {columns.map(col => (
                                                    <th key={col} className="px-4 py-3 font-bold text-slate-300 uppercase tracking-tighter whitespace-nowrap bg-slate-800/80">
                                                        {col}
                                                    </th>
                                                ))}
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-slate-800/50">
                                            {tableData.map((row, i) => (
                                                <tr key={i} className="hover:bg-slate-800/20 transition-colors">
                                                    {columns.map(col => (
                                                        <td key={`${i}-${col}`} className="px-4 py-2.5 text-slate-400 font-mono truncate max-w-[200px]">
                                                            {row[col]?.toString() ?? <span className="text-slate-700 italic">null</span>}
                                                        </td>
                                                    ))}
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                                <div className="p-3 border-t border-slate-800 bg-slate-950/20 flex justify-between items-center shrink-0">
                                    <div className="text-[10px] text-slate-500 font-mono">
                                        [EMPIRICAL FEEDBACK] LOADED {tableData.length} ROWS
                                    </div>
                                    <div className="flex items-center gap-4">
                                        <div className="flex items-center gap-1">
                                            <Button variant="ghost" size="icon" className="h-6 w-6 text-slate-600 disabled:opacity-30" disabled>
                                                <ChevronLeft className="h-4 w-4" />
                                            </Button>
                                            <span className="text-xs text-slate-500 px-2">Page 1</span>
                                            <Button variant="ghost" size="icon" className="h-6 w-6 text-slate-600 disabled:opacity-30" disabled>
                                                <ChevronRight className="h-4 w-4" />
                                            </Button>
                                        </div>
                                    </div>
                                </div>
                            </>
                        )}
                    </CardContent>
                </Card>
            </div>

            {schema && selectedTable && (
                <Card className="shrink-0 border-slate-800 bg-black/40 mt-2">
                    <CardHeader className="py-2 px-4 border-b border-slate-800">
                        <div className="text-[10px] text-slate-500 uppercase font-bold tracking-widest">Table definition (SQL)</div>
                    </CardHeader>
                    <CardContent className="p-3 p-4">
                        <pre className="text-[11px] text-blue-300 font-mono overflow-auto max-h-[100px] leading-relaxed">
                            {schema}
                        </pre>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
