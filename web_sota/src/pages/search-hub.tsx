import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { callTool } from "@/common/api";

export function SearchHub() {
  const [query, setQuery] = useState("");
  const [libraryPath, setLibraryPath] = useState("");
  const [browser, setBrowser] = useState("firefox");
  const [limit, setLimit] = useState(25);
  const [offset, setOffset] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const mediaMutation = useMutation({
    mutationFn: () =>
      callTool("media_library", {
        operation: "search_calibre_fts_db",
        library_path: libraryPath,
        search_query: query,
        include_metadata: true,
        limit,
        offset,
      }),
    onError: (e: Error) => setError(e.message),
    onSuccess: () => setError(null),
  });

  const bookmarksMutation = useMutation({
    mutationFn: () =>
      callTool("browser_bookmarks", {
        operation: "search_bookmarks",
        browser,
        search_query: query,
        limit,
      }),
    onError: (e: Error) => setError(e.message),
    onSuccess: () => setError(null),
  });

  const runBoth = () => {
    if (!query.trim()) {
      setError("Enter a search query.");
      return;
    }
    mediaMutation.mutate();
    bookmarksMutation.mutate();
  };

  const mediaResult = mediaMutation.data?.result;
  const bookmarkResult = bookmarksMutation.data?.result;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Search Hub</h2>
        <p className="text-slate-400">Unified search across Calibre and browser bookmarks.</p>
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white">Query</CardTitle>
          <CardDescription className="text-slate-400">Run cross-domain search with pagination.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-2">
          <input
            className="h-10 rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100"
            placeholder="Search query"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <input
            className="h-10 rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100"
            placeholder="Calibre library path"
            value={libraryPath}
            onChange={(e) => setLibraryPath(e.target.value)}
          />
          <select
            className="h-10 rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100"
            value={browser}
            onChange={(e) => setBrowser(e.target.value)}
          >
            <option value="firefox">firefox</option>
            <option value="chrome">chrome</option>
            <option value="edge">edge</option>
            <option value="brave">brave</option>
          </select>
          <div className="flex gap-2">
            <input
              type="number"
              className="h-10 w-1/2 rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100"
              value={limit}
              min={1}
              max={500}
              onChange={(e) => setLimit(Number(e.target.value || 25))}
            />
            <input
              type="number"
              className="h-10 w-1/2 rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100"
              value={offset}
              min={0}
              onChange={(e) => setOffset(Number(e.target.value || 0))}
            />
          </div>
          <div className="md:col-span-2">
            <Button className="bg-blue-600 hover:bg-blue-700" onClick={runBoth}>
              Search both sources
            </Button>
          </div>
          {error && <p className="md:col-span-2 text-sm text-red-400">{error}</p>}
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white">Calibre FTS</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="max-h-[420px] overflow-auto rounded border border-slate-800 bg-slate-900/40 p-3 text-xs text-slate-300">
              {JSON.stringify(mediaResult ?? { note: "Run search to populate." }, null, 2)}
            </pre>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white">Browser Bookmarks</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="max-h-[420px] overflow-auto rounded border border-slate-800 bg-slate-900/40 p-3 text-xs text-slate-300">
              {JSON.stringify(bookmarkResult ?? { note: "Run search to populate." }, null, 2)}
            </pre>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
