import { useState, useCallback } from 'react';
import { RetinaScan, AnalysisResult } from '../types/retina';
import { config } from '../lib/config';

export const useRetinaAnalysis = () => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);

  const analyzeScan = useCallback(async (scan: RetinaScan): Promise<AnalysisResult> => {
    setIsAnalyzing(true);
    setProgress(0);

    const progressInterval = setInterval(() => {
      setProgress(prev => {
        const newProgress = prev + Math.random() * 10;
        return newProgress >= 90 ? 90 : newProgress;
      });
    }, 500);

    try {
      // If backend API is configured, use it; otherwise fall back to mock
      if (config.api.baseUrl && scan.image instanceof File) {
        const formData = new FormData();
        formData.append('image', scan.image);

        const response = await fetch(`${config.api.baseUrl}/api/predict`, {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          const errJson = await response.json().catch(() => ({} as any));
          const message = (errJson && (errJson.error || errJson.detail)) || `Request failed with ${response.status}`;
          throw new Error(message);
        }

        const data = await response.json();

        // Map backend response to AnalysisResult
        const severityMap: Record<number, AnalysisResult['severity']> = {
          0: 'none',
          1: 'mild',
          2: 'moderate',
          3: 'severe',
          4: 'proliferative',
        };

        const confidencePct = typeof data.confidence === 'number' && data.confidence <= 1 ? data.confidence * 100 : data.confidence || 0;

        const rec = data.recommendation ? [String(data.recommendation)] : [];
        const topFindings: string[] = [];
        if (data.probabilities && typeof data.probabilities === 'object') {
          const entries = Object.entries(data.probabilities) as Array<[string, number]>;
          entries
            .sort((a, b) => b[1] - a[1])
            .slice(0, 3)
            .forEach(([label, prob]) => topFindings.push(`${label}: ${(prob * 100).toFixed(1)}%`));
        } else if (data.class_probabilities) {
          const entries = Object.entries(data.class_probabilities) as Array<[string, number]>;
          entries
            .sort((a, b) => b[1] - a[1])
            .slice(0, 3)
            .forEach(([label, prob]) => topFindings.push(`${label}: ${(prob * 100).toFixed(1)}%`));
        }

        const mapped: AnalysisResult = {
          id: `result_${Date.now()}`,
          scanId: scan.id,
          patientId: scan.patientId,
          confidence: confidencePct || 0,
          severity: severityMap[data.severity_level as number] ?? 'moderate',
          findings: topFindings.length ? topFindings : ['AI findings available in report'],
          recommendations: rec.length ? rec : ['Follow-up per clinician guidance'],
          riskScore: typeof data.confidence === 'number' ? (data.confidence <= 1 ? data.confidence * 100 : data.confidence) : 50,
          processedDate: new Date().toISOString(),
          highlightedAreas: [],
        };

        clearInterval(progressInterval);
        setProgress(100);
        return mapped;
      }

      // Fallback mock when no backend is configured or file not available
      await new Promise(resolve => setTimeout(resolve, 3000));
      clearInterval(progressInterval);
      setProgress(100);
      return {
        id: `result_${Date.now()}`,
        scanId: scan.id,
        patientId: scan.patientId,
        confidence: Math.random() * 20 + 80,
        severity: ['none', 'mild', 'moderate', 'severe', 'proliferative'][
          Math.floor(Math.random() * 5)
        ] as AnalysisResult['severity'],
        findings: [
          'Microaneurysms detected',
          'Possible hemorrhages',
          'Mild exudates present',
        ],
        recommendations: [
          'Schedule follow-up in 6 months',
          'Monitor blood sugar levels',
          'Consider ophthalmology referral',
        ],
        riskScore: Math.random() * 100,
        processedDate: new Date().toISOString(),
        highlightedAreas: [
          {
            x: 100,
            y: 150,
            width: 50,
            height: 50,
            type: 'microaneurysm',
            confidence: 0.89,
          },
        ],
      };
    } finally {
      setIsAnalyzing(false);
      clearInterval(progressInterval);
    }
  }, []);

  return { analyzeScan, isAnalyzing, progress };
};


