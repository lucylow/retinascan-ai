import React, { useState } from 'react';
import { Patient, RetinaScan, AnalysisResult } from '../../types/retina';
import { AccessibilityPanel } from '../Accessibility/AccessibilityPanel';
import { useAccessibility } from '../../hooks/useAccessibility';
import { useRole } from '../../contexts/RoleContext';
import { RoleSwitcher } from '../Common/RoleSwitcher';

// Placeholder stubs for PatientInfo and Analysis components
import { AnalysisResults } from '../Results/AnalysisResults';

export const Dashboard: React.FC = () => {
  const [currentPatient, setCurrentPatient] = useState<Patient | null>({
    id: '1',
    name: 'John Doe',
    age: 58,
    gender: 'male',
    diabetesType: 'type2',
    diabetesDuration: 12,
    lastScreening: '2023-06-15',
    riskLevel: 'high',
  });
  const [currentScan, setCurrentScan] = useState<RetinaScan | null>(null);
  const [currentResult, setCurrentResult] = useState<AnalysisResult | null>(null);
  const [activeTab, setActiveTab] = useState<'patient' | 'scan' | 'results'>('scan');
  const [showAccessibility, setShowAccessibility] = useState(false);
  const [loading, setLoading] = useState(true);
  const [aiSummary, setAISummary] = useState<{
    diabeticRetinopathyRisk: string;
    recommendation: string;
    confidence: number;
  } | null>(null);

  const { settings, updateSettings } = useAccessibility();
  const { role } = useRole();

  React.useEffect(() => {
    const timer = setTimeout(() => {
      setAISummary({
        diabeticRetinopathyRisk: 'Moderate',
        recommendation: 'Follow-up in 3 months with ophthalmologist',
        confidence: 0.89,
      });
      setLoading(false);
    }, 600);
    return () => clearTimeout(timer);
  }, []);

  const handleScanUpload = (scan: RetinaScan) => {
    setCurrentScan(scan);
    setActiveTab('results');
  };

  return (
    <div className={`min-h-screen bg-gray-50 transition-colors duration-300 ${
      settings.highContrast ? 'high-contrast bg-white' : ''
    }`}>
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <img className="h-8 w-auto" src="/logo.png" alt="RetinaScan AI" />
              </div>
              <h1 className="ml-3 text-2xl font-bold text-gray-900">
                RetinaScan <span className="text-blue-600">AI</span>
              </h1>
            </div>

            <div className="flex items-center space-x-4">
              <RoleSwitcher />
              <button
                onClick={() => setShowAccessibility(true)}
                className="p-2 text-gray-600 hover:text-gray-900 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label="Accessibility settings"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
                </svg>
              </button>

              <button
                onClick={() => {
                  setCurrentScan(null);
                  setCurrentResult(null);
                  setActiveTab('scan');
                }}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                New Analysis
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <header className="mb-4">
            <h2 className="text-lg font-semibold text-gray-900">
              Welcome {role === 'clinician' ? 'Doctor' : currentPatient?.name}
            </h2>
            <p className="text-sm text-gray-600">{currentPatient?.lastScreening ? `Last Visit: ${new Date(currentPatient.lastScreening).toLocaleDateString()}` : 'No previous visit recorded'}</p>
          </header>

          {loading && (
            <div className="mb-6 text-gray-600">Loading patient dashboard...</div>
          )}
          <div className="border-b border-gray-200 mb-6">
            <nav className="-mb-px flex space-x-8">
              {[
                { id: 'patient', name: 'Patient Info', icon: '👤' },
                { id: 'scan', name: 'Retina Scan', icon: '📷' },
                { id: 'results', name: 'Analysis Results', icon: '🔍' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <span>{tab.icon}</span>
                  <span>{tab.name}</span>
                </button>
              ))}
            </nav>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            {activeTab === 'scan' && (
              <div className="p-8 text-center text-gray-700">
                Use the header’s "Start Retina Scan" to upload retina images.
              </div>
            )}
            {activeTab === 'results' && (
              <AnalysisResults
                patient={currentPatient}
                scan={currentScan}
                result={currentResult}
                onResultUpdate={setCurrentResult as any}
              />
            )}
            {activeTab === 'patient' && (
              <div className="p-8 text-gray-600">
                {role === 'clinician' ? (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">Clinician Overview</h3>
                    <div className="text-sm mb-4">AI summary available below for quick decision support.</div>
                    {/* Inline summary for clinician */}
                    {aiSummary && (
                      <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                        <div className="font-medium text-blue-900">Retinopathy Risk: {aiSummary.diabeticRetinopathyRisk}</div>
                        <div className="text-blue-900">Recommendation: {aiSummary.recommendation}</div>
                        <div className="text-blue-900">Confidence: {(aiSummary.confidence * 100).toFixed(1)}%</div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">Your Health Overview</h3>
                    <div className="text-sm">Thanks for using RetinaScan AI. Your latest results will appear here.</div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>

      <AccessibilityPanel
        settings={settings}
        onSettingsChange={updateSettings}
        isOpen={showAccessibility}
        onClose={() => setShowAccessibility(false)}
      />

      <div aria-live="polite" aria-atomic="true" className="sr-only">
        {activeTab === 'patient' && 'Patient information tab selected'}
        {activeTab === 'scan' && 'Retina scan upload tab selected'}
        {activeTab === 'results' && 'Analysis results tab selected'}
      </div>
    </div>
  );
};


