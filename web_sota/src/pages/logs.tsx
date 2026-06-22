import {
  ArrowDown,
  ArrowUp,
  Download,
  Radio,
  ScrollText,
  Trash2,
} from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import {
  clearLogs,
  downloadLogsExport,
  getLogStats,
  type LogEntry,
  type LogQueryParams,
  type LogStats,
  queryLogs,
} from "@/common/api";
import { cn } from "@/common/utils";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const LEVELS = ["", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] as const;
const KINDS = ["", "tool_call", "export", "server", "system"] as const;
const PAGE_SIZES = [25, 50, 100, 200] as const;

const selectClass =
  "h-9 w-full rounded-md border border-slate-700 bg-slate-900/80 px-3 text-sm text-slate-200";

function levelTone(level: string): string {
  const l = level.toUpperCase();
  if (l === "ERROR" || l === "CRITICAL")
    return "text-rose-400 bg-rose-500/10 border-rose-500/30";
  if (l === "WARNING")
    return "text-amber-400 bg-amber-500/10 border-amber-500/30";
  if (l === "INFO") return "text-sky-400 bg-sky-500/10 border-sky-500/30";
  if (l === "DEBUG")
    return "text-slate-400 bg-slate-500/10 border-slate-500/30";
  return "text-slate-400 bg-slate-800/50 border-slate-700";
}

function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

export function LogsPage() {
  const [entries, setEntries] = useState<LogEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [maxEntries, setMaxEntries] = useState(2000);
  const [stats, setStats] = useState<LogStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [pageSize, setPageSize] = useState(50);
  const [page, setPage] = useState(0);
  const [level, setLevel] = useState("");
  const [kind, setKind] = useState("");
  const [search, setSearch] = useState("");
  const [searchDraft, setSearchDraft] = useState("");
  const [sort, setSort] = useState<"asc" | "desc">("desc");
  const [liveTail, setLiveTail] = useState(true);

  const streamRef = useRef<HTMLDivElement>(null);
  const newestIdRef = useRef<string | null>(null);
  const userScrolledRef = useRef(false);

  const queryParams = useCallback((): LogQueryParams => {
    const base: LogQueryParams = {
      limit: pageSize,
      offset: page * pageSize,
      sort,
    };
    if (level) base.level = level;
    if (kind) base.kind = kind;
    if (search.trim()) base.search = search.trim();
    return base;
  }, [page, pageSize, level, kind, search, sort]);

  const load = useCallback(async () => {
    try {
      const [logsRes, statsRes] = await Promise.all([
        queryLogs(queryParams()),
        getLogStats(),
      ]);
      setEntries(logsRes.entries);
      setTotal(logsRes.total);
      setMaxEntries(logsRes.max_entries);
      if (logsRes.entries.length > 0 && sort === "desc") {
        newestIdRef.current = logsRes.entries[0].id;
      }
      setStats(statsRes);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load logs");
    } finally {
      setLoading(false);
    }
  }, [queryParams, sort]);

  const tailPoll = useCallback(async () => {
    if (!liveTail || page !== 0 || sort !== "desc") return;
    try {
      const params = queryParams();
      params.limit = pageSize;
      params.offset = 0;
      if (newestIdRef.current) params.after_id = newestIdRef.current;
      const res = await queryLogs(params);
      if (res.entries.length === 0) return;
      newestIdRef.current = res.entries[0].id;
      setEntries((prev) => {
        const merged = [...res.entries, ...prev];
        const seen = new Set<string>();
        const deduped: LogEntry[] = [];
        for (const row of merged) {
          if (seen.has(row.id)) continue;
          seen.add(row.id);
          deduped.push(row);
        }
        return deduped.slice(0, pageSize);
      });
      setTotal((t) => t + res.entries.length);
    } catch {
      /* non-fatal */
    }
  }, [liveTail, page, pageSize, queryParams, sort]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    if (!liveTail) return undefined;
    const id = window.setInterval(() => {
      void tailPoll();
    }, 1500);
    return () => window.clearInterval(id);
  }, [liveTail, tailPoll]);

  useEffect(() => {
    const el = streamRef.current;
    if (!el || userScrolledRef.current) return;
    el.scrollTop = sort === "desc" ? 0 : el.scrollHeight;
  }, [entries, sort]);

  const onStreamScroll = () => {
    const el = streamRef.current;
    if (!el) return;
    userScrolledRef.current = el.scrollTop >= 48;
  };

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <div className="flex items-center gap-2 text-blue-400">
            <ScrollText className="h-6 w-6" />
            <span className="text-sm font-medium uppercase tracking-wider">
              Operations
            </span>
          </div>
          <h2 className="mt-1 text-3xl font-bold tracking-tight text-white">
            Event logs
          </h2>
          <p className="text-slate-400">
            Tool calls, queries, and server events — ring buffer with live tail
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            className="border-slate-700"
            onClick={() =>
              void downloadLogsExport("json", {
                level: level || undefined,
                kind: kind || undefined,
                search: search.trim() || undefined,
                sort,
              })
            }
          >
            <Download className="mr-2 h-4 w-4" />
            JSON
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="border-slate-700"
            onClick={() =>
              void downloadLogsExport("csv", {
                level: level || undefined,
                kind: kind || undefined,
                search: search.trim() || undefined,
                sort,
              })
            }
          >
            <Download className="mr-2 h-4 w-4" />
            CSV
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="border-rose-900/50 text-rose-300 hover:bg-rose-950/40"
            onClick={() => {
              if (!window.confirm("Clear all in-memory log entries?")) return;
              void clearLogs().then(() => {
                newestIdRef.current = null;
                setPage(0);
                void load();
              });
            }}
          >
            <Trash2 className="mr-2 h-4 w-4" />
            Clear
          </Button>
        </div>
      </div>

      {stats && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {[
            { label: "Buffered", value: stats.total.toLocaleString() },
            { label: "Capacity", value: stats.max_entries.toLocaleString() },
            {
              label: "Errors",
              value: (
                (stats.by_level.ERROR ?? 0) + (stats.by_level.CRITICAL ?? 0)
              ).toLocaleString(),
            },
            {
              label: "Tool calls",
              value: (stats.by_kind.tool_call ?? 0).toLocaleString(),
            },
          ].map((item) => (
            <Card
              key={item.label}
              className="border-slate-800 bg-gradient-to-br from-slate-950/80 to-slate-900/40"
            >
              <CardContent className="pt-4">
                <p className="text-xs uppercase tracking-wide text-slate-500">
                  {item.label}
                </p>
                <p className="text-2xl font-semibold text-white">
                  {item.value}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Card className="border-slate-800 bg-slate-950/60 backdrop-blur">
        <CardHeader className="pb-3">
          <CardTitle className="text-white">Filters</CardTitle>
          <CardDescription className="text-slate-400">
            Search and filter — live tail on page 1 when enabled
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6">
            <div className="space-y-1.5">
              <Label className="text-slate-400">Search</Label>
              <Input
                placeholder="tool name, error…"
                value={searchDraft}
                onChange={(e) => setSearchDraft(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    setSearch(searchDraft);
                    setPage(0);
                  }
                }}
                className="border-slate-700 bg-slate-900/80"
              />
            </div>
            <div className="space-y-1.5">
              <Label className="text-slate-400">Level</Label>
              <select
                className={selectClass}
                value={level}
                onChange={(e) => {
                  setLevel(e.target.value);
                  setPage(0);
                }}
              >
                <option value="">All levels</option>
                {LEVELS.filter(Boolean).map((lv) => (
                  <option key={lv} value={lv}>
                    {lv}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-1.5">
              <Label className="text-slate-400">Kind</Label>
              <select
                className={selectClass}
                value={kind}
                onChange={(e) => {
                  setKind(e.target.value);
                  setPage(0);
                }}
              >
                <option value="">All kinds</option>
                {KINDS.filter(Boolean).map((k) => (
                  <option key={k} value={k}>
                    {k}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-1.5">
              <Label className="text-slate-400">Page size</Label>
              <select
                className={selectClass}
                value={pageSize}
                onChange={(e) => {
                  setPageSize(Number(e.target.value));
                  setPage(0);
                }}
              >
                {PAGE_SIZES.map((n) => (
                  <option key={n} value={n}>
                    {n} rows
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-1.5">
              <Label className="text-slate-400">Sort</Label>
              <Button
                variant="outline"
                className="w-full justify-between border-slate-700 bg-slate-900/80"
                onClick={() => {
                  setSort((s) => (s === "desc" ? "asc" : "desc"));
                  setPage(0);
                }}
              >
                {sort === "desc" ? "Newest first" : "Oldest first"}
                {sort === "desc" ? (
                  <ArrowDown className="h-4 w-4" />
                ) : (
                  <ArrowUp className="h-4 w-4" />
                )}
              </Button>
            </div>
            <div className="flex items-end pb-0.5">
              <label className="flex cursor-pointer items-center gap-2 text-sm text-slate-300">
                <input
                  type="checkbox"
                  checked={liveTail}
                  onChange={(e) => setLiveTail(e.target.checked)}
                  className="rounded border-slate-600"
                />
                <Radio
                  className={cn(
                    "h-4 w-4",
                    liveTail ? "text-emerald-400" : "text-slate-600",
                  )}
                />
                Live tail
              </label>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button
              size="sm"
              onClick={() => {
                setSearch(searchDraft);
                setPage(0);
                void load();
              }}
            >
              Apply filters
            </Button>
            <Button
              size="sm"
              variant="ghost"
              className="text-slate-400"
              onClick={() => {
                setSearchDraft("");
                setSearch("");
                setLevel("");
                setKind("");
                setPage(0);
              }}
            >
              Reset
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card className="overflow-hidden border-slate-800 bg-slate-950/80">
        <CardHeader className="flex flex-row items-center justify-between border-b border-slate-800 py-3">
          <div>
            <CardTitle className="text-base text-white">Log stream</CardTitle>
            <CardDescription className="text-xs text-slate-500">
              {total.toLocaleString()} matching · max{" "}
              {maxEntries.toLocaleString()} retained
              {liveTail && page === 0 && (
                <span className="ml-2 text-emerald-400">● tail active</span>
              )}
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {error && (
            <p className="border-b border-rose-900/50 bg-rose-950/30 px-4 py-2 text-sm text-rose-300">
              {error}
            </p>
          )}
          <div
            ref={streamRef}
            onScroll={onStreamScroll}
            className="max-h-[min(58vh,520px)] overflow-y-auto font-mono text-xs leading-relaxed"
          >
            {loading && entries.length === 0 ? (
              <p className="p-6 text-slate-500">Loading logs…</p>
            ) : entries.length === 0 ? (
              <p className="p-6 text-slate-500">
                No entries match your filters.
              </p>
            ) : (
              entries.map((entry) => (
                <div
                  key={entry.id}
                  className="grid grid-cols-[auto_auto_1fr] gap-x-3 border-b border-slate-800/80 px-4 py-2 hover:bg-slate-900/60"
                >
                  <time className="whitespace-nowrap text-slate-500">
                    {formatTime(entry.timestamp)}
                  </time>
                  <span
                    className={cn(
                      "rounded border px-1.5 py-0.5 text-[10px] font-semibold uppercase",
                      levelTone(entry.level),
                    )}
                  >
                    {entry.level}
                  </span>
                  <div className="min-w-0 text-slate-200">
                    <span className="text-violet-400">[{entry.kind}]</span>{" "}
                    {entry.detail}
                    {entry.meta && Object.keys(entry.meta).length > 0 && (
                      <span className="mt-0.5 block truncate text-slate-500">
                        {JSON.stringify(entry.meta)}
                      </span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
          <div className="flex flex-wrap items-center justify-between gap-2 border-t border-slate-800 px-4 py-3 text-sm text-slate-400">
            <span>
              Page {page + 1} of {totalPages}
            </span>
            <div className="flex gap-2">
              <Button
                size="sm"
                variant="outline"
                className="border-slate-700"
                disabled={page <= 0}
                onClick={() => setPage((p) => Math.max(0, p - 1))}
              >
                Previous
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="border-slate-700"
                disabled={page + 1 >= totalPages}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
