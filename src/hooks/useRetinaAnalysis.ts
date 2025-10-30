import { useState, useCallback } from 'react';
import { RetinaScan, AnalysisResult } from '../types/retina';

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
      await new Promise(resolve => setTimeout(resolve, 3000));

      clearInterval(progressInterval);
      setProgress(100);

      const result: AnalysisResult = {
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

      return result;
    } finally {
      setIsAnalyzing(false);
      clearInterval(progressInterval);
    }
  }, []);

  return { analyzeScan, isAnalyzing, progress };
};


