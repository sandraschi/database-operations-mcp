import {
    Card,
    CardContent,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
    Search,
    Database,
    RefreshCw,
    Hash,
    Clock,
    Trash2
} from "lucide-react";

export default function NoSQLManager() {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">NoSQL Manager</h2>
                    <p className="text-slate-400">Browse and manage Redis key-value stores</p>
                </div>
                <Button variant="outline" className="border-slate-800 bg-slate-900/50 hover:bg-slate-800">
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Flush Cache
                </Button>
            </div>

            <div className="flex gap-4">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                    <Input
                        placeholder="Filter keys (e.g. user:*)"
                        className="pl-10 bg-slate-950 border-slate-800 focus:ring-blue-500"
                    />
                </div>
                <Button className="bg-blue-600 hover:bg-blue-700 text-white">SCAN</Button>
            </div>

            <div className="grid gap-4">
                <KeyItem
                    name="user:session:sandra99"
                    type="hash"
                    ttl="14:22"
                    value={'{"id": "sand..."}'}
                />
                <KeyItem
                    name="mcp:system:registry"
                    type="string"
                    ttl="Persistent"
                    value="v1.2.1-prod"
                />
                <KeyItem
                    name="queue:pending_tasks"
                    type="list"
                    ttl="2:45"
                    value="[3 items]"
                />
            </div>
        </div>
    );
}

function KeyItem({ name, type, ttl, value }: { name: string, type: string, ttl: string, value: string }) {
    return (
        <Card className="border-slate-800 bg-slate-950/50 hover:bg-slate-900/50 transition-colors">
            <CardContent className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <div className="bg-slate-900 p-2 rounded border border-slate-800">
                        <Database className="h-4 w-4 text-blue-400" />
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <span className="font-mono text-sm font-bold text-slate-200">{name}</span>
                            <Badge variant="outline" className="text-[10px] uppercase border-slate-700 text-slate-400 h-4">
                                {type}
                            </Badge>
                        </div>
                        <div className="flex items-center gap-3 mt-1 text-xs text-slate-500">
                            <div className="flex items-center gap-1">
                                <Clock className="h-3 w-3" />
                                <span>TTL: {ttl}</span>
                            </div>
                            <div className="flex items-center gap-1">
                                <Hash className="h-3 w-3" />
                                <span>{value}</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="flex gap-2">
                    <Button variant="ghost" size="icon" className="hover:bg-red-900/20 hover:text-red-500 h-8 w-8">
                        <Trash2 className="h-4 w-4" />
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
}
