import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { DATABASE_TYPES_HELP } from "@/common/database-types-help";
import { BookOpen } from "lucide-react";

export function DatabaseTypesHelp() {
    return (
        <div className="space-y-8">
            <div>
                <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                    <BookOpen className="h-7 w-7 text-amber-500" />
                    Database types
                </h2>
                <p className="text-slate-400 mt-1">What each type is, when to use it, and how to connect</p>
            </div>

            <div className="space-y-8">
                {DATABASE_TYPES_HELP.map((db) => (
                    <Card key={db.id} className="border-slate-800 bg-slate-950/50">
                        <CardHeader>
                            <CardTitle className="text-white">{db.name}</CardTitle>
                            <CardDescription className="text-slate-300">{db.shortDescription}</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            <div>
                                <h4 className="text-sm font-medium text-slate-200 mb-1">What it is</h4>
                                <p className="text-slate-400 text-sm leading-relaxed">{db.description}</p>
                            </div>

                            <div>
                                <h4 className="text-sm font-medium text-slate-200 mb-2">When to use it</h4>
                                <ul className="list-disc list-inside text-slate-400 text-sm space-y-1">
                                    {db.whenToUse.map((item, i) => (
                                        <li key={i}>{item}</li>
                                    ))}
                                </ul>
                            </div>

                            <div>
                                <h4 className="text-sm font-medium text-slate-200 mb-2">Required connection fields</h4>
                                <ul className="space-y-2">
                                    {db.requiredFields.map((f) => (
                                        <li key={f.key} className="text-sm">
                                            <span className="font-mono text-slate-300">{f.label}</span>
                                            <span className="text-slate-500 mx-2">—</span>
                                            <span className="text-slate-400">{f.description}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            {db.optionalFields && db.optionalFields.length > 0 && (
                                <div>
                                    <h4 className="text-sm font-medium text-slate-200 mb-2">Optional fields</h4>
                                    <ul className="space-y-2">
                                        {db.optionalFields.map((f) => (
                                            <li key={f.key} className="text-sm">
                                                <span className="font-mono text-slate-300">{f.label}</span>
                                                <span className="text-slate-500 mx-2">—</span>
                                                <span className="text-slate-400">{f.description}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            <div>
                                <h4 className="text-sm font-medium text-slate-200 mb-2">Examples</h4>
                                <ul className="space-y-1">
                                    {db.examples.map((ex, i) => (
                                        <li key={i} className="font-mono text-xs text-slate-400 bg-slate-900/50 rounded px-2 py-1 border border-slate-800">
                                            {ex}
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            <div>
                                <h4 className="text-sm font-medium text-slate-200 mb-2">Tips</h4>
                                <ul className="list-disc list-inside text-slate-400 text-sm space-y-1">
                                    {db.tips.map((tip, i) => (
                                        <li key={i}>{tip}</li>
                                    ))}
                                </ul>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    );
}
