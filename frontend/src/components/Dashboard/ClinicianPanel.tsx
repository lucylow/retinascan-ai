import React from 'react';
import { Patient } from '../../types/retina';
import { AutoSaveNote } from '../Common/AutoSaveNote';
import { fetchClinicalGuidelines, getBatchResults, ClinicalBatchItem } from '../../lib/demoApi';

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

  const [guidelines, setGuidelines] = React.useState<string>('');
  const [batch, setBatch] = React.useState<ClinicalBatchItem[]>([]);

  React.useEffect(() => {
    let mounted = true;
    (async () => {
      const [g, b] = await Promise.all([
        fetchClinicalGuidelines(),
        getBatchResults(),
      ]);
      if (!mounted) return;
      setGuidelines(g);
      setBatch(b);
    })();
    return () => {
      mounted = false;
    };
  }, []);

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
        <h3 className="text-lg font-semibold text-gray-900">Clinical Guidelines Summary</h3>
        <pre className="mt-2 whitespace-pre-line text-sm bg-gray-50 border border-gray-200 rounded-md p-3 max-h-40 overflow-y-auto">
{guidelines}
        </pre>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-gray-900">Recent Patients (Batch)</h3>
        <div className="mt-3 overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="text-left text-gray-600">
              <tr>
                <th className="py-2 pr-4">Patient</th>
                <th className="py-2 pr-4">Age</th>
                <th className="py-2 pr-4">History</th>
                <th className="py-2 pr-4">DR Grade</th>
                <th className="py-2 pr-4">Confidence</th>
                <th className="py-2 pr-4">Referral</th>
                <th className="py-2 pr-0">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {batch.map((p) => (
                <tr key={p.patientId}>
                  <td className="py-2 pr-4">{p.name}</td>
                  <td className="py-2 pr-4">{p.age}</td>
                  <td className="py-2 pr-4">
                    <ul className="list-disc pl-4">
                      {p.history.map((h, i) => (
                        <li key={i}>{h}</li>
                      ))}
                    </ul>
                  </td>
                  <td className="py-2 pr-4">
                    <span className={`px-2 py-0.5 rounded text-xs ${p.drGrade === 'No DR' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>{p.drGrade}</span>
                  </td>
                  <td className="py-2 pr-4">{(p.confidence * 100).toFixed(1)}%</td>
                  <td className="py-2 pr-4">
                    <span className={`px-2 py-0.5 rounded text-xs ${p.referralRequired ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>{p.referralRequired ? 'Yes' : 'No'}</span>
                  </td>
                  <td className="py-2 pr-0 whitespace-nowrap">
                    <button onClick={() => alert(`Adding note for ${p.name}`)} className="text-blue-700 hover:underline mr-3">Add Notes</button>
                    <button onClick={() => alert(`Requesting referral for ${p.name}`)} className="text-yellow-700 hover:underline">Send Referral</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-gray-900">Clinical Notes</h3>
        <AutoSaveNote storageKey={`notes_${patient.id}`} />
      </div>
    </section>
  );
};


