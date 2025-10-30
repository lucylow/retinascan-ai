import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/hooks/use-toast';
import { useEHRIntegration } from '@/hooks/useEHRIntegration';
import { AnalysisResult } from '@/types/retina';
import {
  Hospital,
  Upload,
  User,
  AlertCircle,
  CheckCircle,
  Loader2,
  Activity,
} from 'lucide-react';

interface EHRIntegrationPanelProps {
  analysisResult: AnalysisResult;
  imageData?: string | File;
  patientId?: string;
}

export function EHRIntegrationPanel({
  analysisResult,
  imageData,
  patientId,
}: EHRIntegrationPanelProps) {
  const [localPatientId, setLocalPatientId] = useState(patientId || '');
  const [patientData, setPatientData] = useState<any>(null);
  const [conditions, setConditions] = useState<any[]>([]);
  const [submissionResult, setSubmissionResult] = useState<any>(null);
  const [showPatientInfo, setShowPatientInfo] = useState(false);
  const [base64Image, setBase64Image] = useState<string>('');

  // Convert File to base64 if needed
  useEffect(() => {
    const convertImageToBase64 = async () => {
      if (imageData instanceof File) {
        const reader = new FileReader();
        reader.onloadend = () => {
          const result = reader.result as string;
          // Remove data URL prefix if present
          const base64 = result.includes(',') ? result.split(',')[1] : result;
          setBase64Image(base64);
        };
        reader.readAsDataURL(imageData);
      } else if (typeof imageData === 'string') {
        setBase64Image(imageData);
      }
    };

    convertImageToBase64();
  }, [imageData]);

  const { toast } = useToast();
  const {
    submitToEHR,
    getPatientDemographics,
    getPatientConditions,
    isSubmitting,
    isLoadingPatient,
  } = useEHRIntegration();

  useEffect(() => {
    if (localPatientId) {
      loadPatientData();
    }
  }, [localPatientId]);

  const loadPatientData = async () => {
    if (!localPatientId) return;

    const demographics = await getPatientDemographics(localPatientId);
    if (demographics) {
      setPatientData(demographics);
      setShowPatientInfo(true);

      const patientConditions = await getPatientConditions(localPatientId);
      setConditions(patientConditions);

      toast({
        title: 'Patient found',
        description: 'Patient data loaded from EHR',
      });
    } else {
      toast({
        title: 'Patient not found',
        description: 'Could not find patient in EHR system',
        variant: 'destructive',
      });
    }
  };

  const handleSubmitToEHR = async () => {
    if (!localPatientId) {
      toast({
        title: 'Patient ID required',
        description: 'Please enter a patient ID',
        variant: 'destructive',
      });
      return;
    }

    const result = await submitToEHR(analysisResult, base64Image, localPatientId);

    if (result.success) {
      setSubmissionResult(result);
      toast({
        title: 'Successfully submitted',
        description: 'Results have been sent to the EHR system',
      });
    } else {
      toast({
        title: 'Submission failed',
        description: result.error || 'Failed to submit to EHR',
        variant: 'destructive',
      });
    }
  };

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      none: 'bg-green-500',
      mild: 'bg-yellow-500',
      moderate: 'bg-orange-500',
      severe: 'bg-red-500',
      proliferative: 'bg-red-700',
    };
    return colors[severity] || 'bg-gray-500';
  };

  const getUrgencyBadge = (severity: string) => {
    const urgency: Record<string, string> = {
      none: 'Routine',
      mild: 'Non-urgent',
      moderate: 'Semi-urgent',
      severe: 'Urgent',
      proliferative: 'Emergency',
    };
    return urgency[severity] || 'Unknown';
  };

  return (
    <Card className="p-6 space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <Hospital className="h-5 w-5 text-blue-600" />
        <h3 className="text-lg font-semibold">EHR Integration</h3>
      </div>

      {/* Patient ID Input */}
      <div className="space-y-2">
        <label className="text-sm font-medium">Patient ID</label>
        <div className="flex gap-2">
          <input
            type="text"
            value={localPatientId}
            onChange={(e) => setLocalPatientId(e.target.value)}
            placeholder="Enter patient ID from EHR"
            className="flex-1 px-3 py-2 border rounded-md"
            disabled={isLoadingPatient}
          />
          <Button
            onClick={loadPatientData}
            disabled={!localPatientId || isLoadingPatient}
            variant="outline"
          >
            {isLoadingPatient ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <User className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>

      {/* Patient Information */}
      {showPatientInfo && patientData && (
        <Card className="p-4 bg-blue-50 border-blue-200">
          <div className="flex items-center gap-2 mb-3">
            <CheckCircle className="h-4 w-4 text-blue-600" />
            <span className="font-semibold text-blue-900">Patient Information</span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>
              <span className="text-gray-600">Name:</span> {patientData.name}
            </div>
            <div>
              <span className="text-gray-600">DOB:</span> {patientData.birth_date}
            </div>
            <div>
              <span className="text-gray-600">Gender:</span> {patientData.gender}
            </div>
            {conditions.length > 0 && (
              <div>
                <span className="text-gray-600">Conditions:</span> {conditions.length}
              </div>
            )}
          </div>

          {conditions.length > 0 && (
            <div className="mt-3 pt-3 border-t border-blue-200">
              <span className="text-xs font-medium text-gray-600">Conditions:</span>
              <div className="flex flex-wrap gap-1 mt-2">
                {conditions.slice(0, 3).map((cond) => (
                  <Badge key={cond.id} variant="outline" className="text-xs">
                    {cond.display}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </Card>
      )}

      {/* Analysis Summary */}
      <Card className="p-4 bg-gray-50">
        <div className="flex items-center justify-between mb-3">
          <span className="font-semibold">Analysis Summary</span>
          <Badge className={`${getSeverityColor(analysisResult.severity)} text-white`}>
            {analysisResult.severity.toUpperCase()}
          </Badge>
        </div>
        <div className="space-y-2">
          <div>
            <span className="text-sm text-gray-600">Confidence:</span>
            <Progress value={analysisResult.confidence} className="h-2 mt-1" />
            <span className="text-xs text-gray-500">
              {analysisResult.confidence.toFixed(1)}%
            </span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Urgency:</span>
            <Badge variant="outline">{getUrgencyBadge(analysisResult.severity)}</Badge>
          </div>
        </div>
      </Card>

      {/* Submission Result */}
      {submissionResult && submissionResult.success && (
        <Card className="p-4 bg-green-50 border-green-200">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle className="h-5 w-5 text-green-600" />
            <span className="font-semibold text-green-900">Successfully Submitted</span>
          </div>
          <div className="text-sm space-y-1">
            {submissionResult.observation_id && (
              <div>
                <span className="text-gray-600">Observation ID:</span>{' '}
                {submissionResult.observation_id}
              </div>
            )}
            {submissionResult.report_id && (
              <div>
                <span className="text-gray-600">Report ID:</span> {submissionResult.report_id}
              </div>
            )}
            {submissionResult.timestamp && (
              <div className="text-xs text-gray-500 mt-2">
                Submitted: {new Date(submissionResult.timestamp).toLocaleString()}
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Error Message */}
      {submissionResult && !submissionResult.success && (
        <Card className="p-4 bg-red-50 border-red-200">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-red-600" />
            <div>
              <span className="font-semibold text-red-900">Submission Failed</span>
              <p className="text-sm text-red-700 mt-1">{submissionResult.error}</p>
            </div>
          </div>
        </Card>
      )}

      {/* Submit Button */}
      <Button
        onClick={handleSubmitToEHR}
        disabled={!localPatientId || isSubmitting || !showPatientInfo}
        className="w-full"
        size="lg"
      >
        {isSubmitting ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Submitting to EHR...
          </>
        ) : (
          <>
            <Upload className="mr-2 h-4 w-4" />
            Submit to EHR System
          </>
        )}
      </Button>

      {!localPatientId && (
        <p className="text-xs text-center text-gray-500">
          Enter a patient ID to enable EHR submission
        </p>
      )}

      {localPatientId && !showPatientInfo && !isLoadingPatient && (
        <div className="flex items-center gap-2 text-sm text-amber-600 bg-amber-50 p-3 rounded">
          <AlertCircle className="h-4 w-4" />
          <span>Please load patient information first</span>
        </div>
      )}
    </Card>
  );
}

