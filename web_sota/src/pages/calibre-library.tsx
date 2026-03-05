import { useState, useMemo, useEffect } from 'react';
import {
    Card,
    CardHeader,
    CardTitle,
    CardContent,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
    Search,
    Filter,
    Table as TableIcon,
    FileText,
    Download,
    Eye,
    RefreshCw,
    MoreHorizontal,
    ArrowUp,
    ArrowDown,
    ArrowUpDown,
    Book,
    User,
    ChevronLeft,
    ChevronRight,
} from "lucide-react";
import { cn } from "@/common/utils";

interface BookData {
    id: number;
    title: string;
    author_sort: string;
    isbn: string;
    path: string;
    pubdate: string;
    series_index: number;
    timestamp: string;
    last_modified: string;
}

export default function CalibreLibrary() {
    const [books, setBooks] = useState<BookData[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");
    const [sortConfig, setSortConfig] = useState<{ key: keyof BookData; direction: 'asc' | 'desc' } | null>(null);
    const [currentPage, setCurrentPage] = useState(1);
    const booksPerPage = 10;

    useEffect(() => {
        fetchBooks();
    }, []);

    const fetchBooks = async () => {
        setLoading(true);
        try {
            // @ts-ignore - Tool call to mcp-server
            const result = await window.mcp.callTool('database-operations-mcp', 'sqlite_get_table_data', {
                db_path: 'C:/Users/sandr/Desktop/Calibre Library/metadata.db',
                table_name: 'books',
                limit: 1000
            });
            if (result.success) {
                setBooks(result.data);
            }
        } catch (error) {
            console.error("Failed to fetch books:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleSort = (key: keyof BookData) => {
        let direction: 'asc' | 'desc' = 'asc';
        if (sortConfig && sortConfig.key === key && sortConfig.direction === 'asc') {
            direction = 'desc';
        }
        setSortConfig({ key, direction });
    };

    const filteredBooks = useMemo(() => {
        return books.filter(book =>
            book.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
            book.author_sort.toLowerCase().includes(searchTerm.toLowerCase())
        );
    }, [books, searchTerm]);

    const sortedBooks = useMemo(() => {
        const sortableItems = [...filteredBooks];
        if (sortConfig !== null) {
            sortableItems.sort((a, b) => {
                const aValue = a[sortConfig.key];
                const bValue = b[sortConfig.key];
                if (aValue < bValue) {
                    return sortConfig.direction === 'asc' ? -1 : 1;
                }
                if (aValue > bValue) {
                    return sortConfig.direction === 'asc' ? 1 : -1;
                }
                return 0;
            });
        }
        return sortableItems;
    }, [filteredBooks, sortConfig]);

    const currentBooks = useMemo(() => {
        const indexOfLastBook = currentPage * booksPerPage;
        const indexOfFirstBook = indexOfLastBook - booksPerPage;
        return sortedBooks.slice(indexOfFirstBook, indexOfLastBook);
    }, [sortedBooks, currentPage]);

    const totalPages = Math.ceil(sortedBooks.length / booksPerPage);

    return (
        <div className="flex flex-col gap-6 p-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-slate-100 tracking-tight">Calibre Library</h1>
                    <p className="text-slate-400 mt-1">Direct SQLite interface to metadata.db</p>
                </div>
                <Button variant="outline" className="gap-2" onClick={fetchBooks}>
                    <RefreshCw className={cn("h-4 w-4", loading && "animate-spin")} />
                    Refresh
                </Button>
            </div>

            <Card className="border-slate-800 bg-slate-900/50 backdrop-blur-xl">
                <CardHeader className="border-b border-slate-800 pb-4">
                    <div className="flex items-center justify-between">
                        <CardTitle className="text-xl font-semibold flex items-center gap-2">
                            <Book className="h-5 w-5 text-blue-500" />
                            Library Catalog
                        </CardTitle>
                        <div className="flex items-center gap-3">
                            <div className="relative">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                                <Input
                                    placeholder="Search library..."
                                    className="pl-9 w-64 bg-slate-950/50 border-slate-800 focus:ring-blue-500"
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                />
                            </div>
                            <Button variant="ghost" size="icon" className="text-slate-400 hover:text-white">
                                <Filter className="h-4 w-4" />
                            </Button>
                        </div>
                    </div>
                </CardHeader>
                <CardContent className="p-0">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm border-collapse">
                            <thead>
                                <tr className="border-b border-slate-800 bg-slate-800/30">
                                    <th className="px-6 py-4 font-medium text-slate-400 uppercase tracking-wider w-12 text-center">ID</th>
                                    <th
                                        className="px-6 py-4 font-medium text-slate-400 uppercase tracking-wider cursor-pointer hover:text-blue-400 transition-colors"
                                        onClick={() => handleSort('title')}
                                    >
                                        <div className="flex items-center gap-2">
                                            Title
                                            {sortConfig?.key === 'title' ? (
                                                sortConfig.direction === 'asc' ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />
                                            ) : <ArrowUpDown className="h-3 w-3 opacity-30" />}
                                        </div>
                                    </th>
                                    <th
                                        className="px-6 py-4 font-medium text-slate-400 uppercase tracking-wider cursor-pointer hover:text-blue-400 transition-colors"
                                        onClick={() => handleSort('author_sort')}
                                    >
                                        <div className="flex items-center gap-2">
                                            Author
                                            {sortConfig?.key === 'author_sort' ? (
                                                sortConfig.direction === 'asc' ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />
                                            ) : <ArrowUpDown className="h-3 w-3 opacity-30" />}
                                        </div>
                                    </th>
                                    <th className="px-6 py-4 font-medium text-slate-400 uppercase tracking-wider">Path</th>
                                    <th className="px-6 py-4 font-medium text-slate-400 uppercase tracking-wider text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800">
                                {loading && books.length === 0 ? (
                                    <tr>
                                        <td colSpan={5} className="px-6 py-12 text-center text-slate-500 italic">
                                            <div className="flex flex-col items-center gap-2">
                                                <RefreshCw className="h-8 w-8 animate-spin text-blue-500 opacity-50" />
                                                Streaming library data...
                                            </div>
                                        </td>
                                    </tr>
                                ) : currentBooks.length === 0 ? (
                                    <tr>
                                        <td colSpan={5} className="px-6 py-12 text-center text-slate-500 italic">No books matching your criteria</td>
                                    </tr>
                                ) : currentBooks.map((book) => (
                                    <tr key={book.id} className="group hover:bg-slate-800/30 transition-colors">
                                        <td className="px-6 py-4 text-slate-500 font-mono text-center">{book.id}</td>
                                        <td className="px-6 py-4 text-slate-200 font-medium">{book.title}</td>
                                        <td className="px-6 py-4 text-slate-300">
                                            <div className="flex items-center gap-2">
                                                <User className="h-3 w-3 text-slate-500" />
                                                {book.author_sort}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-slate-400 font-mono text-xs truncate max-w-xs">{book.path}</td>
                                        <td className="px-6 py-4 text-right">
                                            <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                                <Button variant="ghost" size="icon" className="h-8 w-8 text-blue-400 hover:bg-blue-500/10">
                                                    <Eye className="h-4 w-4" />
                                                </Button>
                                                <Button variant="ghost" size="icon" className="h-8 w-8 text-slate-400 hover:text-white">
                                                    <MoreHorizontal className="h-4 w-4" />
                                                </Button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    <div className="flex items-center justify-between border-t border-slate-800 p-4">
                        <p className="text-xs text-slate-500">
                            Showing {Math.min(currentBooks.length, booksPerPage)} of {sortedBooks.length} entries
                        </p>
                        <div className="flex items-center gap-2">
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                                disabled={currentPage === 1}
                                className="h-8 border-slate-800 bg-transparent text-slate-400"
                            >
                                <ChevronLeft className="h-4 w-4 mr-1" />
                                Previous
                            </Button>
                            <div className="flex h-8 items-center px-3 text-sm text-slate-300 border border-slate-800 rounded-md bg-slate-950/50">
                                {currentPage} / {totalPages || 1}
                            </div>
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                                disabled={currentPage === totalPages || totalPages === 0}
                                className="h-8 border-slate-800 bg-transparent text-slate-400"
                            >
                                Next
                                <ChevronRight className="h-4 w-4 ml-1" />
                            </Button>
                        </div>
                    </div>
                </CardContent>
            </Card>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card className="border-slate-800 bg-slate-900/50 p-6 flex flex-col items-center gap-3 text-center">
                    <TableIcon className="h-8 w-8 text-blue-500" />
                    <div>
                        <h3 className="font-semibold text-slate-100">SQLite Inspector</h3>
                        <p className="text-xs text-slate-400 mt-1">Direct file-system access to metadata.db</p>
                    </div>
                </Card>
                <Card className="border-slate-800 bg-slate-900/50 p-6 flex flex-col items-center gap-3 text-center">
                    <FileText className="h-8 w-8 text-purple-500" />
                    <div>
                        <h3 className="font-semibold text-slate-100">Metadata Extraction</h3>
                        <p className="text-xs text-slate-400 mt-1">SOTA automated extraction from library</p>
                    </div>
                </Card>
                <Card className="border-slate-800 bg-slate-900/50 p-6 flex flex-col items-center gap-3 text-center">
                    <Download className="h-8 w-8 text-green-500" />
                    <div>
                        <h3 className="font-semibold text-slate-100">Export Tools</h3>
                        <p className="text-xs text-slate-400 mt-1">CSV/JSON synchronization utilities</p>
                    </div>
                </Card>
            </div>
        </div>
    );
}
