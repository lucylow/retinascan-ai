import { useState, useCallback } from 'react';
import { config } from '../lib/config';
import { AnalysisResult } from '../types/retina';

interface EHRSubmissionResult {
  success: boolean;
  observation_id?: string;
  report_id?: string;
  audit_id?: string;
  timestamp?: string;
  error?: string;
}

interface PatientDemographics {
  patient_id: string;
  name: string;
  birth_date: string;
  gender: string;
  contact_info: {
    phone?: string;
    email?: string;
    address?: {
      line: string[];
      city: string;
      state: string;
      postal_code: string;
    };
  };
}

interface PatientCondition {
  id: string;
  code: string;
  display: string;
  system: string;
  onset_date: string;
  clinical_status: string;
}

export const useEHRIntegration = () => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoadingPatient, setIsLoadingPatient] = useState(false);

  const submitToEHR = useCallback(
    async (
      analysisResult: AnalysisResult,
      imageData: string,
      patientId: string
    ): Promise<EHRSubmissionResult> => {
      setIsSubmitting(true);

      try {
        // Map frontend result to backend format
        const severityMap: Record<string, number> = {
          none: 0,
          mild: 1,
          moderate: 2,
          severe: 3,
          proliferative: 4,
        };

        const aiResult = {
          diagnosis: `${
            analysisResult.severity.charAt(0).toUpperCase() +
            analysisResult.severity.slice(1)
          } Diabetic Retinopathy`,
          severity_level: severityMap[analysisResult.severity] ?? 0,
          confidence: analysisResult.confidence / 100,
          quality_score: 0.9, // Could be extracted from analysis
          recommendation: analysisResult.recommendations.join('. '),
        };

        const response = await fetch(`${config.api.baseUrl}/api/ehr/submit-results`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            patient_id: patientId,
            ai_result: aiResult,
            image_data: imageData,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.error || `HTTP ${response.status}`);
        }

        const data = await response.json();
        return {
          success: data.success || false,
          observation_id: data.observation_id,
          report_id: data.report_id,
          audit_id: data.audit_id,
          timestamp: data.timestamp,
          error: data.error,
        };
      } catch (error: any) {
        console.error('EHR submission error:', error);
        return {
          success: false,
          error: error.message || 'Failed to submit to EHR',
        };
      } finally {
        setIsSubmitting(false);
      }
    },
    []
  );

  const getPatientDemographics = useCallback(
    async (patientId: string): Promise<PatientDemographics | null> => {
      setIsLoadingPatient(true);

      try {
        const response = await fetch(
          `${config.api.baseUrl}/api/ehr/patient/${patientId}`
        );

        if (!response.ok) {
          if (response.status === 404) {
            console.log('Patient not found in EHR');
            return null;
          }
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        return data.patient || null;
      } catch (error: any) {
        console.error('Error fetching patient demographics:', error);
        return null;
      } finally {
        setIsLoadingPatient(false);
      }
    },
    []
  );

  const getPatientConditions = useCallback(
    async (patientId: string): Promise<PatientCondition[]> => {
      try {
        const response = await fetch(
          `${config.api.baseUrl}/api/ehr/patient/${patientId}/conditions`
        );

        if (!response.ok) {
          console.error('Failed to fetch conditions:', response.status);
          return [];
        }

        const data = await response.json();
        return data.conditions || [];
      } catch (error: any) {
        console.error('Error fetching conditions:', error);
        return [];
      }
    },
    []
  );

  const processWorkflow = useCallback(
    async (
      patientId: string,
      imageData: string,
      workflowConfig?: Record<string, any>
    ): Promise<any> => {
      setIsSubmitting(true);

      try {
        const response = await fetch(`${config.api.baseUrl}/api/ehr/workflow`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            patient_id: patientId,
            image_data: imageData,
            workflow_config: workflowConfig || {},
          }),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.error || `HTTP ${response.status}`);
        }

        return await response.json();
      } catch (error: any) {
        console.error('Workflow error:', error);
        throw error;
      } finally {
        setIsSubmitting(false);
      }
    },
    []
  );

  return {
    submitToEHR,
    getPatientDemographics,
    getPatientConditions,
    processWorkflow,
    isSubmitting,
    isLoadingPatient,
  };
};

