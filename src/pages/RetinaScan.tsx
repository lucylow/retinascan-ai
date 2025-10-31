import React from 'react';
import { Dashboard } from '../components/Dashboard/Dashboard';
import { AccessibilityProvider } from '../contexts/AccessibilityContext';
import { RoleProvider } from '../contexts/RoleContext';

const RetinaScanPage: React.FC = () => {
  return (
    <AccessibilityProvider>
      <RoleProvider>
        <Dashboard />
      </RoleProvider>
    </AccessibilityProvider>
  );
};

export default RetinaScanPage;


