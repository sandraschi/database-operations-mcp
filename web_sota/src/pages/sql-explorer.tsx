import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
    Search,
    Database,
    History as HistoryIcon,
    ChevronRight,
    Play,
    FileJson,
    SearchCheck,
    Table,
} from "lucide-react";

export default function SQLExplorer() {
    return (
        <div className="grid grid-cols-12 gap-6">
            {/* Sidebar: Schema Browser */}
            <div className="col-span-3 space-y-4">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="p-4">
                        <CardTitle className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center justify-between">
                            Schema Browser
                            <Search className="h-3 w-3" />
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="p-0">
                        <SchemaItem label="calibre_library (metadata.db)" items={['books', 'authors', 'tags', 'series', 'ratings', 'comments']} />
                        <SchemaItem label="core_system" items={['config', 'audit_logs']} />
                        <SchemaItem label="mcp_registry" items={['servers', 'tools']} />
                    </CardContent>
                </Card>
            </div>

            {/* Main: Query Editor & Results */}
            <div className="col-span-9 space-y-6">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between py-2 border-b border-slate-800">
                        <Tabs defaultValue="query1">
                            <TabsList className="bg-transparent gap-2">
                                <TabsTrigger value="query1" className="text-xs data-[state=active]:bg-slate-800">New Query *</TabsTrigger>
                                <TabsTrigger value="query2" className="text-xs">Analytics Users</TabsTrigger>
                            </TabsList>
                        </Tabs>
                        <div className="flex gap-2">
                            <Button size="sm" variant="ghost" className="text-slate-400">
                                <HistoryIcon className="h-4 w-4" />
                            </Button>
                            <Button size="sm" className="bg-emerald-600 hover:bg-emerald-700 text-white">
                                <Play className="h-3 w-3 mr-2" />
                                Run Query
                            </Button>
                        </div>
                    </CardHeader>
                    <CardContent className="p-4">
                        <div className="font-mono text-sm min-h-[150px] bg-black/30 rounded p-4 text-emerald-400/80">
                            SELECT b.id, b.title, a.name as author <br />
                            FROM books b <br />
                            JOIN books_authors_link bal ON b.id = bal.book <br />
                            JOIN authors a ON bal.author = a.id <br />
                            ORDER BY b.timestamp DESC <br />
                            LIMIT 5;
                        </div>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="py-2 border-b border-slate-800 flex flex-row items-center justify-between">
                        <CardTitle className="text-xs font-bold uppercase text-slate-400">Results</CardTitle>
                        <div className="flex gap-2">
                            <Button size="sm" variant="ghost" className="h-6 text-[10px] gap-1">
                                <FileJson className="h-3 w-3" /> JSON
                            </Button>
                            <Button size="sm" variant="ghost" className="h-6 text-[10px] gap-1">
                                <SearchCheck className="h-3 w-3" /> CSV
                            </Button>
                        </div>
                    </CardHeader>
                    <CardContent className="p-0">
                        <table className="w-full text-xs text-left">
                            <thead className="bg-slate-900/50 text-slate-500 uppercase tracking-wider font-bold">
                                <tr>
                                    <th className="px-4 py-2 border-b border-slate-800">id</th>
                                    <th className="px-4 py-2 border-b border-slate-800">title</th>
                                    <th className="px-4 py-2 border-b border-slate-800">author</th>
                                </tr>
                            </thead>
                            <tbody className="text-slate-300">
                                <tr className="hover:bg-slate-800/30">
                                    <td className="px-4 py-2 border-b border-slate-900 font-mono">1</td>
                                    <td className="px-4 py-2 border-b border-slate-900">Foundations of Materialism</td>
                                    <td className="px-4 py-2 border-b border-slate-900">Sandra Schipal</td>
                                </tr>
                                <tr className="hover:bg-slate-800/30">
                                    <td className="px-4 py-2 border-b border-slate-900 font-mono">2</td>
                                    <td className="px-4 py-2 border-b border-slate-900">Reductionist Logic for AI</td>
                                    <td className="px-4 py-2 border-b border-slate-900">Sandra Schipal</td>
                                </tr>
                            </tbody>
                        </table>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}

function SchemaItem({ label, items }: { label: string, items: string[] }) {
    return (
        <div className="group">
            <div className="flex items-center gap-2 px-4 py-2 hover:bg-slate-900 cursor-pointer transition-colors text-slate-200">
                <ChevronRight className="h-3 w-3 text-slate-500 group-hover:rotate-90 transition-transform" />
                <Database className="h-3.5 w-3.5 text-blue-500" />
                <span className="text-sm font-medium">{label}</span>
            </div>
            <div className="hidden group-hover:block ml-8 border-l border-slate-800">
                {items.map(item => (
                    <div key={item} className="flex items-center gap-2 px-4 py-1.5 hover:text-white text-slate-500 text-xs transition-colors cursor-pointer capitalize">
                        <Table className="h-3 w-3" />
                        {item}
                    </div>
                ))}
            </div>
        </div>
    );
}
