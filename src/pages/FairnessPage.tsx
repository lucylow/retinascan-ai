/**
 * Fairness Page
 * Main page for displaying bias and fairness monitoring
 */

import React from 'react';
import { FairnessMonitor } from '../components/Fairness/FairnessMonitor';

const FairnessPage: React.FC = () => {
  return (
    <div className="min-h-screen">
      <div className="container mx-auto py-8">
        <div className="mb-6">
          <h1 className="text-4xl font-bold mb-2">Bias & Fairness Monitoring</h1>
          <p className="text-gray-600 text-lg">
            Comprehensive monitoring of AI model fairness across all patient demographics
          </p>
        </div>
        <FairnessMonitor />
      </div>
    </div>
  );
};

export default FairnessPage;
