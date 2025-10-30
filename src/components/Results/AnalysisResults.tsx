import React from 'react';
import { Patient, RetinaScan, AnalysisResult } from '../../types/retina';

interface AnalysisResultsProps {
  patient: Patient | null;
  scan: RetinaScan | null;
  result: AnalysisResult | null;
  onResultUpdate?: (result: AnalysisResult) => void;
}

export const AnalysisResults: React.FC<AnalysisResultsProps> = ({ patient, scan, result }) => {
  if (!patient || !scan) {
    return (
      <div className="p-8 text-center">
        <div className="text-gray-500 text-lg mb-4">Complete patient information and upload a scan to view results</div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="p-8 text-center">
        <div className="animate-pulse">
          <div className="text-gray-500 text-lg mb-4">Analyzing retina scan...</div>
          <div className="w-64 h-3 bg-gray-200 rounded-full mx-auto mb-2"></div>
          <div className="w-48 h-3 bg-gray-200 rounded-full mx-auto"></div>
        </div>
      </div>
    );
  }

  const getSeverityColor = (severity: string) => {
    const colors = {
      none: 'bg-green-100 text-green-800',
      mild: 'bg-blue-100 text-blue-800',
      moderate: 'bg-yellow-100 text-yellow-800',
      severe: 'bg-orange-100 text-orange-800',
      proliferative: 'bg-red-100 text-red-800',
    } as const;
    return (colors as any)[severity] || colors.none;
  };

  const getRiskLevel = (score: number) => {
    if (score < 20) return { level: 'Low', color: 'text-green-600' };
    if (score < 50) return { level: 'Moderate', color: 'text-yellow-600' };
    if (score < 80) return { level: 'High', color: 'text-orange-600' };
    return { level: 'Very High', color: 'text-red-600' };
  };

  const riskInfo = getRiskLevel(result.riskScore);

  const downloadBlob = (blob: Blob, filename: string) => {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  };

  const handleDownloadReport = () => {
    const report = {
      meta: {
        generatedAt: new Date().toISOString(),
        app: 'RetinaScan AI',
        version: '1.0',
      },
      patient,
      scan: {
        id: scan.id,
        patientId: scan.patientId,
        uploadDate: scan.uploadDate,
        eye: scan.eye,
        quality: scan.quality,
      },
      result,
    };
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const safeName = `${patient.name || 'patient'}-${scan.id}`.replace(/[^a-z0-9-_]/gi, '_');
    downloadBlob(blob, `retina-report-${safeName}.json`);
  };

  const handleScheduleFollowUp = () => {
    const now = new Date();
    const days = result.riskScore >= 80 ? 14 : result.riskScore >= 50 ? 30 : 90;
    const start = new Date(now.getTime() + days * 24 * 60 * 60 * 1000);
    const end = new Date(start.getTime() + 30 * 60 * 1000);
    const dt = (d: Date) => d.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
    const ics = [
      'BEGIN:VCALENDAR',
      'VERSION:2.0',
      'PRODID:-//RetinaScan AI//EN',
      'CALSCALE:GREGORIAN',
      'METHOD:PUBLISH',
      'BEGIN:VEVENT',
      `UID:${scan.id}@retinascan.ai`,
      `DTSTAMP:${dt(new Date())}`,
      `DTSTART:${dt(start)}`,
      `DTEND:${dt(end)}`,
      `SUMMARY:Follow-up: RetinaScan for ${patient.name}`,
      `DESCRIPTION:Severity: ${result.severity} | Risk: ${riskInfo.level} (${result.riskScore.toFixed(1)}) | Confidence: ${result.confidence.toFixed(1)}%`,
      'END:VEVENT',
      'END:VCALENDAR',
    ].join('\r\n');
    const blob = new Blob([ics], { type: 'text/calendar;charset=utf-8' });
    const safeName = `${patient.name || 'patient'}-${scan.id}`.replace(/[^a-z0-9-_]/gi, '_');
    downloadBlob(blob, `retina-followup-${safeName}.ics`);
  };

  const handleShare = async () => {
    const summary = `RetinaScan AI Result\n` +
      `Patient: ${patient.name}\n` +
      `Severity: ${result.severity}\n` +
      `Risk: ${riskInfo.level} (${result.riskScore.toFixed(1)})\n` +
      `Confidence: ${result.confidence.toFixed(1)}%\n` +
      `Scan ID: ${scan.id}`;

    if (navigator.share) {
      try {
        await navigator.share({ title: 'RetinaScan AI Result', text: summary });
        return;
      } catch (_) {}
    }

    const mailto = `mailto:?subject=${encodeURIComponent('RetinaScan AI Result')}&body=${encodeURIComponent(summary)}`;
    window.location.href = mailto;
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Analysis Results</h2>
        <p className="text-gray-600">AI-powered assessment of diabetic retinopathy risk</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Severity Level</h3>
          <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium capitalize ${getSeverityColor(result.severity)}`}>{result.severity}</div>
          <div className="mt-3 text-3xl font-bold text-gray-900">{result.confidence.toFixed(1)}%</div>
          <div className="text-sm text-gray-600">Confidence Score</div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Risk Assessment</h3>
          <div className={`text-2xl font-bold ${riskInfo.color} mb-2`}>{riskInfo.level} Risk</div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div className="bg-blue-600 h-3 rounded-full transition-all duration-500" style={{ width: `${result.riskScore}%` }} />
          </div>
          <div className="text-sm text-gray-600 mt-2">Risk Score: {result.riskScore.toFixed(1)}/100</div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Patient Summary</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between"><span className="text-gray-600">Age:</span><span className="font-medium">{patient.age}</span></div>
            <div className="flex justify-between"><span className="text-gray-600">Diabetes Duration:</span><span className="font-medium">{patient.diabetesDuration} years</span></div>
            <div className="flex justify-between"><span className="text-gray-600">Last Screening:</span><span className="font-medium">{patient.lastScreening ? new Date(patient.lastScreening).toLocaleDateString() : 'Never'}</span></div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Findings</h3>
          <ul className="space-y-3">
            {result.findings.map((finding, index) => (
              <li key={index} className="flex items-start">
                <div className="flex-shrink-0 w-2 h-2 bg-blue-600 rounded-full mt-2 mr-3"></div>
                <span className="text-gray-700">{finding}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommendations</h3>
          <ul className="space-y-3">
            {result.recommendations.map((recommendation, index) => (
              <li key={index} className="flex items-start">
                <div className="flex-shrink-0 w-2 h-2 bg-green-600 rounded-full mt-2 mr-3"></div>
                <span className="text-gray-700">{recommendation}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="mt-8 flex flex-wrap gap-4">
        <button onClick={handleDownloadReport} className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">Download Full Report</button>
        <button onClick={handleScheduleFollowUp} className="bg-green-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-green-700 transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2">Schedule Follow-up</button>
        <button onClick={handleShare} className="bg-gray-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-gray-700 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2">Share with Specialist</button>
      </div>

      <div className="mt-8 bg-gray-50 border border-gray-200 rounded-lg p-4">
        <p className="text-sm text-gray-600 text-center">
          <strong>Disclaimer:</strong> This AI analysis is intended to assist healthcare professionals and should not replace clinical judgment. Always verify results with comprehensive medical evaluation.
        </p>
      </div>
    </div>
  );
};


