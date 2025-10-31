import { useCallback, useMemo, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/hooks/use-toast";
import { config } from "@/lib/config";

type ImageStatus = "pending" | "processing" | "completed" | "error";

interface RetinalImageItem {
  id: string;
  file: File;
  preview: string;
  status: ImageStatus;
  result?: any;
  error?: string;
}

export default function AIAnalyzer() {
  const [images, setImages] = useState<RetinalImageItem[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [batchProgress, setBatchProgress] = useState(0);
  const [completedCount, setCompletedCount] = useState(0);
  const { toast } = useToast();

  const handleFileUpload = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    if (files.length === 0) return;

    const newImages: RetinalImageItem[] = files.map((file) => ({
      id: `${Date.now()}-${Math.random()}`,
      file,
      preview: URL.createObjectURL(file),
      status: "pending",
    }));
    setImages((prev) => [...prev, ...newImages]);
  }, []);

  const processBatchImages = useCallback(async () => {
    if (images.length === 0) {
      toast({ title: "No images to process", description: "Please upload images first." });
      return;
    }

    setIsProcessing(true);
    setCompletedCount(0);
    setBatchProgress(0);

    const updated = [...images];

    for (let i = 0; i < updated.length; i++) {
      const img = updated[i];
      if (img.status === "completed" || img.status === "error") continue;

      updated[i] = { ...img, status: "processing" };
      setImages([...updated]);

      try {
        const formData = new FormData();
        // FastAPI endpoint expects field name 'file'
        formData.append("file", img.file);

        const response = await fetch(`${config.api.baseUrl}/api/predict`, {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          const err = await response.json().catch(() => ({} as any));
          throw new Error(err?.detail || err?.error || `Request failed: ${response.status}`);
        }

        const data = await response.json();
        updated[i] = { ...updated[i], status: "completed", result: data };
        setCompletedCount((c) => c + 1);
      } catch (e: any) {
        updated[i] = { ...updated[i], status: "error", error: e?.message || "Analysis failed" };
      }

      setBatchProgress(((i + 1) / updated.length) * 100);
      setImages([...updated]);
    }

    setIsProcessing(false);
    toast({ title: "Batch analysis complete" });
  }, [images, toast]);

  const completedWithResults = useMemo(
    () => images.filter((i) => i.status === "completed" && i.result),
    [images]
  );

  const summary = useMemo(() => {
    if (completedWithResults.length === 0) return null as
      | null
      | {
          totalAnalyzed: number;
          avgConfidence: string;
          requiresReferral: number;
          analysisDate: string;
        };

    const avgConfidence =
      completedWithResults.reduce((sum, i) => sum + (Number(i.result?.confidence) || 0), 0) /
      completedWithResults.length;

    const requiresReferral = completedWithResults.filter((i) => {
      // Heuristic: refer if severity_class >= 2 or explicit flag present
      const sev = Number(i.result?.severity_class);
      return Boolean(i.result?.requiresReferral) || (Number.isFinite(sev) && sev >= 2);
    }).length;

    return {
      totalAnalyzed: completedWithResults.length,
      avgConfidence: (avgConfidence * 100).toFixed(1),
      requiresReferral,
      analysisDate: new Date().toISOString(),
    };
  }, [completedWithResults]);

  const exportCSV = useCallback(() => {
    if (completedWithResults.length === 0) return;
    const rows = [
      [
        "Image ID",
        "Severity Class",
        "Severity Level",
        "Confidence",
        "Label",
        "Recommendation",
        "Referral Needed",
      ],
      ...completedWithResults.map((i) => [
        i.id,
        String(i.result?.severity_class ?? ""),
        String(i.result?.severity_level ?? ""),
        ((Number(i.result?.confidence) || 0) * 100).toFixed(1),
        String(i.result?.label ?? ""),
        String(i.result?.recommendation ?? ""),
        (Number(i.result?.severity_class) ?? 0) >= 2 || i.result?.requiresReferral ? "Yes" : "No",
      ]),
    ];

    const csv = rows.map((r) => r.map((v) => `${String(v).replace(/"/g, '""')}`).join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `retinascan-report-${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }, [completedWithResults]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      <section className="container mx-auto px-4 py-10 md:py-16">
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold">AI Retinal Image Dashboard</h1>
          <p className="text-muted-foreground mt-2">
            Upload multiple images, track progress, and review results.
          </p>
        </div>

        <Card className="p-6 mb-8">
          <div className="flex flex-col md:flex-row md:items-center gap-4">
            <input
              type="file"
              multiple
              accept="image/*"
              onChange={handleFileUpload}
              disabled={isProcessing}
            />
            <div className="text-sm text-muted-foreground">{images.length} images selected</div>
            <div className="md:ml-auto flex gap-3">
              <Button onClick={processBatchImages} disabled={images.length === 0 || isProcessing}>
                {isProcessing ? "Analyzing Images..." : "Analyze All Images"}
              </Button>
              <Button variant="outline" onClick={exportCSV} disabled={completedWithResults.length === 0}>
                Export CSV
              </Button>
            </div>
          </div>
        </Card>

        {isProcessing && (
          <div className="mb-8">
            <div className="flex items-center justify-between mb-2 text-sm">
              <span>
                Processing: {completedCount}/{images.length}
              </span>
              <span>{Math.round(batchProgress)}%</span>
            </div>
            <Progress value={batchProgress} className="h-4" />
          </div>
        )}

        {summary && (
          <Card className="p-6 mb-8">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <div className="text-sm text-muted-foreground">Total Analyzed</div>
                <div className="text-2xl font-semibold">{summary.totalAnalyzed}</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Avg Confidence</div>
                <div className="text-2xl font-semibold">{summary.avgConfidence}%</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Require Referral</div>
                <div className="text-2xl font-semibold text-red-600">{summary.requiresReferral}</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Analysis Date</div>
                <div className="text-sm">{new Date(summary.analysisDate).toLocaleDateString()}</div>
              </div>
            </div>
          </Card>
        )}

        <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
          {images.map((image) => (
            <Card key={image.id} className="p-4">
              <div className="space-y-3">
                <div className="w-full h-60 bg-muted rounded-md overflow-hidden relative">
                  <img
                    src={image.preview}
                    alt="retinal"
                    className="w-full h-full object-cover"
                  />
                  {image.status === "processing" && (
                    <div className="absolute inset-0 bg-black/40 flex items-center justify-center text-white text-sm">
                      Processing...
                    </div>
                  )}
                </div>

                <div className="flex items-center justify-between">
                  <span
                    className={
                      "text-xs font-medium px-2 py-1 rounded-full " +
                      (image.status === "completed"
                        ? "bg-green-100 text-green-700"
                        : image.status === "error"
                        ? "bg-red-100 text-red-700"
                        : image.status === "processing"
                        ? "bg-blue-100 text-blue-700"
                        : "bg-gray-100 text-gray-700")
                    }
                  >
                    {image.status.toUpperCase()}
                  </span>
                </div>

                {image.result && (
                  <div className="text-sm space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">Severity:</span>
                      <span>{String(image.result?.severity_level ?? "-")}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="font-medium">Confidence:</span>
                      <span>{((Number(image.result?.confidence) || 0) * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="font-medium">Label:</span>
                      <span className="truncate max-w-[60%] text-right" title={String(image.result?.label ?? "")}>{String(image.result?.label ?? "-")}</span>
                    </div>
                    {image.result?.recommendation && (
                      <div className="text-xs text-muted-foreground mt-2">
                        {String(image.result.recommendation)}
                      </div>
                    )}
                  </div>
                )}

                {image.error && (
                  <div className="text-xs text-red-600 bg-red-50 border border-red-100 rounded-md p-2">
                    {image.error}
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
}


