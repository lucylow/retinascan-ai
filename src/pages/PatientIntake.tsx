import React from 'react';
import PatientHealthIntake, { PatientIntakeData } from '../components/Patient/PatientHealthIntake';
import { AccessibilityProvider } from '../contexts/AccessibilityContext';
import { RoleProvider } from '../contexts/RoleContext';
import { config } from '../lib/config';

const PatientIntakePage: React.FC = () => {
  const handleSubmit = (data: PatientIntakeData) => {
    // Submit to backend intake endpoint if available
    if (config.api.baseUrl) {
      fetch(`${config.api.baseUrl}/api/intake`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patientId: 'demo-patient', form: data }),
      }).catch(() => {});
    }
  };

  return (
    <AccessibilityProvider>
      <RoleProvider>
        <PatientHealthIntake onSubmit={handleSubmit} />
      </RoleProvider>
    </AccessibilityProvider>
  );
};

export default PatientIntakePage;


