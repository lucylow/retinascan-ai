import React, { useState } from 'react';
import AIVisualization from '@/components/AIVisualization';

export default function RetinaDataViz() {
  const [diagnosisResult, setDiagnosisResult] = useState<any | null>(null);
  const [visualizations, setVisualizations] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalysis = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/predict/detailed', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (!response.ok || !data.success) throw new Error(data?.detail || data?.error || 'Request failed');
      setDiagnosisResult(data.prediction);
      setVisualizations(data.visualizations);
    } catch (e: any) {
      setError(e?.message || 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold">AI-Assisted Data Visualization</h1>
          <p className="text-gray-600 mt-1">Upload a retinal image to generate explainable AI visualizations.</p>
        </div>

        <div className="bg-white border rounded-lg p-6 mb-8">
          <input
            type="file"
            accept="image/*"
            onChange={(e) => e.target.files && e.target.files[0] && handleAnalysis(e.target.files[0])}
            disabled={loading}
          />
          {loading && <div className="text-sm text-gray-600 mt-3">Analyzing image…</div>}
          {error && <div className="text-sm text-red-600 mt-3">{error}</div>}
        </div>

        {visualizations && diagnosisResult && (
          <AIVisualization visualizations={visualizations} prediction={diagnosisResult} />
        )}
      </div>
    </div>
  );
}


