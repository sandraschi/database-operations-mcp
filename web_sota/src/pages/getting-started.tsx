import { Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { BookOpen, Database, Table2, LayoutGrid, FileStack, ArrowRight } from "lucide-react";

const STEPS = [
    {
        step: 1,
        title: "Add a connection",
        description: "Register your database (SQLite, PostgreSQL, MySQL, etc.) with a name so the app can talk to it.",
        href: "/connection-wizard",
        icon: Database,
    },
    {
        step: 2,
        title: "Set it active",
        description: "On the Connections page, pick the connection you want to use by default and click \"Set active\".",
        href: "/connections",
        icon: Database,
    },
    {
        step: 3,
        title: "Browse schema and data",
        description: "Use Schema to see databases and tables, and Table viewer to open a table and scroll through rows.",
        href: "/schema",
        icon: Table2,
        altHref: "/table-viewer",
        altLabel: "Table viewer",
    },
    {
        step: 4,
        title: "Run a query",
        description: "Simple query lets you pick table and columns and add a filter without writing SQL. Data lets you run any SELECT.",
        href: "/simple-query",
        icon: LayoutGrid,
        altHref: "/data",
        altLabel: "Data",
    },
    {
        step: 5,
        title: "Export or import",
        description: "Export: run a query, then download JSON or CSV. Import: paste a JSON array or upload a file into a table.",
        href: "/export-import",
        icon: FileStack,
    },
];

const PAGES = [
    { href: "/", label: "Overview", desc: "Service and tool count" },
    { href: "/database-types-help", label: "Database types help", desc: "Detailed help for each DB type" },
    { href: "/connection-wizard", label: "Add connection", desc: "Guided setup for new DBs" },
    { href: "/connections", label: "Connections", desc: "List, test, set active" },
    { href: "/schema", label: "Schema", desc: "Databases, tables, column info" },
    { href: "/table-viewer", label: "Table viewer", desc: "Browse table rows" },
    { href: "/simple-query", label: "Simple query", desc: "Query without SQL" },
    { href: "/data", label: "Data", desc: "Run SQL and quick sample" },
    { href: "/export-import", label: "Export / Import", desc: "Download or bulk insert" },
    { href: "/health", label: "Health", desc: "DB health and metrics" },
    { href: "/tools", label: "Tools", desc: "Call any MCP tool" },
    { href: "/connection-manager", label: "Connection manager", desc: "Register and test DB connections" },
    { href: "/tool-explorer", label: "Tool explorer", desc: "Browse tools by family and capability" },
    { href: "/playground", label: "Playground", desc: "JSON tool runner with history" },
    { href: "/search-hub", label: "Search hub", desc: "Cross-search Calibre and bookmarks" },
    { href: "/jobs-exports", label: "Jobs & Exports", desc: "Track export jobs and outputs" },
    { href: "/mcp-capabilities", label: "MCP capabilities", desc: "Sampling/workflows/skills/prompts status" },
];

export function GettingStarted() {
    return (
        <div className="space-y-8">
            <div>
                <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                    <BookOpen className="h-7 w-7 text-amber-500" />
                    Getting started
                </h2>
                <p className="text-slate-400 mt-1">Typical workflow and what each page does</p>
            </div>

            <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader>
                    <CardTitle className="text-white">Workflow</CardTitle>
                    <CardDescription className="text-slate-400">Do these in order if you are new.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    {STEPS.map((s) => (
                        <div key={s.step} className="flex gap-4">
                            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-slate-800 text-slate-300 font-semibold">
                                {s.step}
                            </div>
                            <div className="flex-1 min-w-0">
                                <div className="flex flex-wrap items-center gap-2">
                                    <Link
                                        to={s.href}
                                        className="font-medium text-blue-400 hover:text-blue-300 hover:underline"
                                    >
                                        {s.title}
                                    </Link>
                                    {s.altHref && (
                                        <>
                                            <span className="text-slate-500">/</span>
                                            <Link to={s.altHref} className="text-slate-400 hover:text-slate-300 hover:underline text-sm">
                                                {s.altLabel}
                                            </Link>
                                        </>
                                    )}
                                    <ArrowRight className="h-4 w-4 text-slate-500" />
                                </div>
                                <p className="text-slate-400 text-sm mt-1">{s.description}</p>
                            </div>
                        </div>
                    ))}
                </CardContent>
            </Card>

            <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader>
                    <CardTitle className="text-white">What’s what</CardTitle>
                    <CardDescription className="text-slate-400">Short guide to each page in the sidebar.</CardDescription>
                </CardHeader>
                <CardContent>
                    <ul className="space-y-3">
                        {PAGES.map((p) => (
                            <li key={p.href} className="flex items-baseline gap-2">
                                <Link to={p.href} className="text-blue-400 hover:text-blue-300 hover:underline font-medium shrink-0">
                                    {p.label}
                                </Link>
                                <span className="text-slate-500">—</span>
                                <span className="text-slate-400 text-sm">{p.desc}</span>
                            </li>
                        ))}
                    </ul>
                </CardContent>
            </Card>
        </div>
    );
}
