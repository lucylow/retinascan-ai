import React from 'react';
import { Patient } from '../../types/retina';

interface PatientPanelProps {
  patient: Patient | null;
  aiSummary?: {
    diabeticRetinopathyRisk: string;
    recommendation: string;
    confidence: number;
  } | null;
}

export const PatientPanel: React.FC<PatientPanelProps> = ({ patient, aiSummary }) => {
  if (!patient) return null;

  return (
    <section className="p-6 space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">Your Health Overview</h2>
        <p className="text-gray-700 mt-2">Thank you for using the RetinaScan AI platform!</p>
      </div>

      {aiSummary && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h3 className="font-semibold text-green-900">Your latest AI screening result</h3>
          <div className="mt-2 grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
            <div><span className="text-green-900 font-medium">Risk Level:</span> {aiSummary.diabeticRetinopathyRisk}</div>
            <div><span className="text-green-900 font-medium">Confidence:</span> {(aiSummary.confidence * 100).toFixed(1)}%</div>
            <div><span className="text-green-900 font-medium">Recommendation:</span> {aiSummary.recommendation}</div>
          </div>
          <button
            onClick={() => alert('Scheduling your next appointment...')}
            className="mt-4 bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
          >
            Schedule Appointment
          </button>
        </div>
      )}

      <footer className="text-xs text-gray-500">RetinaScan AI Platform © {new Date().getFullYear()}</footer>
    </section>
  );
};


