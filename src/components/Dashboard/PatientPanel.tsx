import React from 'react';
import { Patient } from '../../types/retina';
import { getEducationalContent, getNearbyClinics, getLatestPatientResults } from '../../lib/demoApi';
import { Link } from 'react-router-dom';

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

  const [education, setEducation] = React.useState<string>('');
  const [clinics, setClinics] = React.useState<Array<{ id: string; name: string; address: string; phone: string; website: string }>>([]);
  const [latest, setLatest] = React.useState<{ drGrade: string; confidence: number; requiresReferral: boolean } | null>(null);
  const [intakeComplete, setIntakeComplete] = React.useState<boolean>(false);

  React.useEffect(() => {
    let mounted = true;
    (async () => {
      const [edu, near, res] = await Promise.all([
        getEducationalContent(),
        getNearbyClinics(),
        getLatestPatientResults(),
      ]);
      if (!mounted) return;
      setEducation(edu);
      setClinics(near);
      setLatest(res);
      const raw = localStorage.getItem('patient_intake');
      setIntakeComplete(Boolean(raw));
    })();
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <section className="p-6 space-y-6">
      {!intakeComplete && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-yellow-900">Complete Health Intake</h3>
              <p className="text-sm text-yellow-900">Help your clinician by completing a brief health intake before your screening.</p>
            </div>
            <Link to="/intake" className="bg-yellow-600 text-white px-3 py-2 rounded-md hover:bg-yellow-700">Start</Link>
          </div>
        </div>
      )}
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

      {latest && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="font-semibold text-gray-900">Summary</h3>
          <div className="mt-2 text-sm">
            <div>Diabetic Retinopathy Risk: <span className={`px-2 py-0.5 rounded text-xs ${latest.drGrade === 'No DR' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>{latest.drGrade}</span></div>
            <div>Confidence: {(latest.confidence * 100).toFixed(1)}%</div>
            {latest.requiresReferral && (
              <div className="text-red-700 font-medium mt-1">Referral Recommended: Please schedule a visit.</div>
            )}
          </div>
        </div>
      )}

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold text-blue-900">Educational Resources</h3>
        <pre className="mt-2 whitespace-pre-line text-sm text-blue-900">{education}</pre>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-gray-900">Nearby Clinics for Screening</h3>
        <ul className="mt-2 space-y-2 text-sm">
          {clinics.length > 0 ? (
            clinics.map((c) => (
              <li key={c.id}>
                <a href={c.website} target="_blank" rel="noreferrer" className="text-blue-700 hover:underline">
                  {c.name}
                </a>
                <span className="text-gray-600"> — {c.address} — Call: {c.phone}</span>
              </li>
            ))
          ) : (
            <li className="text-gray-600">No clinic data available</li>
          )}
        </ul>
      </div>

      <footer className="text-xs text-gray-500">RetinaScan AI Platform © {new Date().getFullYear()}</footer>
    </section>
  );
};


