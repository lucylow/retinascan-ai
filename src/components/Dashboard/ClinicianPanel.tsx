import React from 'react';
import { Patient } from '../../types/retina';
import { AutoSaveNote } from '../Common/AutoSaveNote';

interface ClinicianPanelProps {
  patient: Patient | null;
  aiSummary?: {
    diabeticRetinopathyRisk: string;
    recommendation: string;
    confidence: number;
  } | null;
}

export const ClinicianPanel: React.FC<ClinicianPanelProps> = ({ patient, aiSummary }) => {
  if (!patient) return null;

  return (
    <section className="p-6 space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">Patient Summary</h2>
        <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
          <div><span className="text-gray-600">Name:</span> <span className="font-medium">{patient.name}</span></div>
          <div><span className="text-gray-600">Age:</span> <span className="font-medium">{patient.age}</span></div>
          <div><span className="text-gray-600">Diabetes Type:</span> <span className="font-medium capitalize">{patient.diabetesType}</span></div>
          <div><span className="text-gray-600">Last Visit:</span> <span className="font-medium">{patient.lastScreening ? new Date(patient.lastScreening).toLocaleDateString() : 'N/A'}</span></div>
        </div>
      </div>

      {aiSummary && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900">AI Analysis</h3>
          <div className="mt-2 grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
            <div><span className="text-blue-900 font-medium">Retinopathy Risk:</span> {aiSummary.diabeticRetinopathyRisk}</div>
            <div><span className="text-blue-900 font-medium">Confidence:</span> {(aiSummary.confidence * 100).toFixed(1)}%</div>
            <div><span className="text-blue-900 font-medium">Recommendation:</span> {aiSummary.recommendation}</div>
          </div>
        </div>
      )}

      <div>
        <h3 className="text-lg font-semibold text-gray-900">Clinical Notes</h3>
        <AutoSaveNote storageKey={`notes_${patient.id}`} />
      </div>
    </section>
  );
};


