import { useMemo, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface ComparativeAnalysisProps {
  results: Array<{
    imageId: string;
    severity_class?: number;
    severity_level?: string;
    confidence?: number;
    label?: string;
    recommendation?: string;
    requiresReferral?: boolean;
  }>;
}

export function ComparativeAnalysis({ results }: ComparativeAnalysisProps) {
  const [view, setView] = useState<"table" | "summary">("summary");

  const summary = useMemo(() => {
    const total = results.length;
    const avgConf =
      total === 0
        ? 0
        : results.reduce((s, r) => s + (Number(r.confidence) || 0), 0) / total;
    const referCount = results.filter((r) => {
      const sev = Number(r.severity_class);
      return Boolean(r.requiresReferral) || (Number.isFinite(sev) && sev >= 2);
    }).length;
    const distribution = results.reduce<Record<string, number>>((acc, r) => {
      const key = String(r.severity_level || "Unknown");
      acc[key] = (acc[key] || 0) + 1;
      return acc;
    }, {});
    return { total, avgConf, referCount, distribution };
  }, [results]);

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Comparative Analysis</h3>
        <div className="flex gap-2">
          <Button variant={view === "summary" ? "default" : "outline"} onClick={() => setView("summary")}>
            Summary
          </Button>
          <Button variant={view === "table" ? "default" : "outline"} onClick={() => setView("table")}>
            Table
          </Button>
        </div>
      </div>

      {view === "summary" && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <div className="text-sm text-muted-foreground">Total Analyzed</div>
            <div className="text-2xl font-semibold">{summary.total}</div>
          </div>
          <div>
            <div className="text-sm text-muted-foreground">Avg Confidence</div>
            <div className="text-2xl font-semibold">{(summary.avgConf * 100).toFixed(1)}%</div>
          </div>
          <div>
            <div className="text-sm text-muted-foreground">Require Referral</div>
            <div className="text-2xl font-semibold text-red-600">{summary.referCount}</div>
          </div>

          <div className="md:col-span-3">
            <div className="text-sm text-muted-foreground mb-2">DR Grade Distribution</div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {Object.entries(summary.distribution).map(([k, v]) => (
                <div key={k} className="flex items-center justify-between rounded-md border p-2 text-sm">
                  <span>{k}</span>
                  <span className="font-medium">{v}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {view === "table" && (
        <div className="w-full overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-muted">
                <th className="text-left p-2">Image ID</th>
                <th className="text-left p-2">Severity</th>
                <th className="text-left p-2">Confidence</th>
                <th className="text-left p-2">Referral</th>
              </tr>
            </thead>
            <tbody>
              {results.map((r) => (
                <tr key={r.imageId} className="border-b">
                  <td className="p-2">{r.imageId.slice(0, 16)}...</td>
                  <td className="p-2">{String(r.severity_level || "-")}</td>
                  <td className="p-2">{((Number(r.confidence) || 0) * 100).toFixed(1)}%</td>
                  <td className="p-2">{(Number(r.severity_class) || 0) >= 2 || r.requiresReferral ? "Yes" : "No"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}


