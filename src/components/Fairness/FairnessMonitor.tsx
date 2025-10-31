/**
 * Fairness Monitor Component
 * Real-time display of bias and fairness metrics for RetinaScan AI
 */

import React, { useState, useEffect } from 'react';
import { FairnessAuditor } from '../../services/FairnessAuditor';
import { TransparencyReporter } from '../../services/TransparencyReporter';
import { DatasetManager } from '../../services/DatasetManager';
import {
  BiasAuditResult,
  FairnessReport,
  DemographicGroup,
  RetinaImageWithDemographics,
} from '../../types/fairness';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';

interface FairnessMonitorProps {
  modelVersion?: string;
}

export const FairnessMonitor: React.FC<FairnessMonitorProps> = () => {
  const [currentAudit, setCurrentAudit] = useState<BiasAuditResult | null>(null);
  const [fairnessReport, setFairnessReport] = useState<FairnessReport | null>(null);
  const [fairnessScore, setFairnessScore] = useState<number>(0);
  const [biasAlerts, setBiasAlerts] = useState<Array<{ severity: string; description: string; subgroup: string }>>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [subgroupPerformance, setSubgroupPerformance] = useState<Record<string, any>>({});

  useEffect(() => {
    const initializeFairnessMonitoring = async () => {
      setLoading(true);
      try {
        const auditor = new FairnessAuditor();
        const reporter = new TransparencyReporter();
        const datasetManager = new DatasetManager();

        // Load diverse datasets
        await datasetManager.loadDiverseDatasets();

        // Generate mock test data for demonstration
        const testData = generateMockTestData();
        const demographicGroups = generateMockDemographicGroups();

        // Generate mock predictions
        const predictions = testData.map((image) => ({
          imageId: image.id,
          predictedLabel: image.label,
          confidence: 0.85 + Math.random() * 0.1,
        }));

        // Perform comprehensive audit
        const audit = await auditor.performComprehensiveAudit(
          predictions,
          testData,
          demographicGroups
        );

        setCurrentAudit(audit);

        // Calculate fairness score
        const score = calculateOverallFairnessScore(audit);
        setFairnessScore(score);

        // Extract bias alerts
        const alerts = audit.biasFlags.map((flag) => ({
          severity: flag.severity,
          description: flag.description,
          subgroup: flag.subgroup,
        }));
        setBiasAlerts(alerts);

        // Set subgroup performance
        setSubgroupPerformance(audit.subgroupMetrics);

        // Generate and set fairness report
        const report = await reporter.generateFairnessReport(audit);
        setFairnessReport(report);
      } catch (error) {
        console.error('Error initializing fairness monitoring:', error);
      } finally {
        setLoading(false);
      }
    };

    initializeFairnessMonitoring();
  }, []);

  const calculateOverallFairnessScore = (audit: BiasAuditResult): number => {
    const metricScore =
      audit.overallMetrics.accuracy * 0.3 +
      (1 - audit.overallMetrics.falsePositiveRate) * 0.2 +
      (1 - audit.overallMetrics.falseNegativeRate) * 0.2 +
      audit.overallMetrics.equalizedOdds * 0.15 +
      audit.overallMetrics.demographicParity * 0.15;

    const highBiasFlags = audit.biasFlags.filter((f) => f.severity === 'high').length;
    const mediumBiasFlags = audit.biasFlags.filter((f) => f.severity === 'medium').length;
    const biasPenalty = highBiasFlags * 0.1 + mediumBiasFlags * 0.05;

    return Math.max(0, Math.min(1, metricScore - biasPenalty));
  };

  const getScoreColor = (score: number): string => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getSeverityColor = (severity: string): string => {
    switch (severity) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'low':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading fairness metrics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fairness-monitor p-6 space-y-6">
      <div className="fairness-header">
        <h2 className="text-3xl font-bold mb-2">AI Fairness & Bias Monitoring</h2>
        <p className="text-gray-600 mb-4">
          Real-time monitoring of equitable performance across all patient demographics
        </p>
        <div className={`fairness-score ${getScoreColor(fairnessScore)} text-2xl font-bold`}>
          Fairness Score: {(fairnessScore * 100).toFixed(1)}%
        </div>
        <Progress value={fairnessScore * 100} className="mt-2 h-2" />
      </div>

      {currentAudit && (
        <Card>
          <CardHeader>
            <CardTitle>Overall Performance Metrics</CardTitle>
            <CardDescription>
              Model performance across all demographic groups
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-gray-600">Accuracy</p>
                <p className="text-2xl font-bold">
                  {(currentAudit.overallMetrics.accuracy * 100).toFixed(1)}%
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">False Positive Rate</p>
                <p className="text-2xl font-bold">
                  {(currentAudit.overallMetrics.falsePositiveRate * 100).toFixed(1)}%
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">False Negative Rate</p>
                <p className="text-2xl font-bold">
                  {(currentAudit.overallMetrics.falseNegativeRate * 100).toFixed(1)}%
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Equalized Odds</p>
                <p className="text-2xl font-bold">
                  {(currentAudit.overallMetrics.equalizedOdds * 100).toFixed(1)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {biasAlerts.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Bias Alerts</CardTitle>
            <CardDescription>
              {biasAlerts.length} bias issue{biasAlerts.length !== 1 ? 's' : ''} detected
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {biasAlerts.map((alert, index) => (
                <div
                  key={index}
                  className={`p-4 rounded-lg border ${getSeverityColor(alert.severity)}`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <Badge className={getSeverityColor(alert.severity)}>
                      {alert.severity.toUpperCase()}
                    </Badge>
                    <span className="text-sm font-medium">{alert.subgroup}</span>
                  </div>
                  <p className="text-sm">{alert.description}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {Object.keys(subgroupPerformance).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Performance by Demographic Group</CardTitle>
            <CardDescription>
              Detailed metrics stratified by patient demographics
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b">
                    <th className="p-3 font-semibold">Demographic Group</th>
                    <th className="p-3 font-semibold">Accuracy</th>
                    <th className="p-3 font-semibold">False Positive Rate</th>
                    <th className="p-3 font-semibold">False Negative Rate</th>
                    <th className="p-3 font-semibold">Fairness Score</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(subgroupPerformance).map(([group, metrics]) => (
                    <tr key={group} className="border-b hover:bg-gray-50">
                      <td className="p-3 font-medium">{group}</td>
                      <td className="p-3">{(metrics.accuracy * 100).toFixed(1)}%</td>
                      <td className="p-3">{(metrics.falsePositiveRate * 100).toFixed(1)}%</td>
                      <td className="p-3">{(metrics.falseNegativeRate * 100).toFixed(1)}%</td>
                      <td className="p-3">
                        <span className={getScoreColor(metrics.equalizedOdds)}>
                          {(metrics.equalizedOdds * 100).toFixed(1)}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {fairnessReport && fairnessReport.recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recommendations</CardTitle>
            <CardDescription>
              Actionable steps to improve model fairness
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {fairnessReport.recommendations.map((rec, index) => (
                <li key={index} className="flex items-start">
                  <span className="mr-2 text-blue-600">•</span>
                  <span className="text-sm">{rec}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {fairnessReport && (
        <Card>
          <CardHeader>
            <CardTitle>Regulatory Compliance</CardTitle>
            <CardDescription>
              Status of regulatory compliance checks
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-medium">FDA Compliance</span>
                <Badge
                  className={
                    fairnessReport.complianceStatus.fda
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }
                >
                  {fairnessReport.complianceStatus.fda ? 'Compliant' : 'Non-Compliant'}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="font-medium">EU MDR Compliance</span>
                <Badge
                  className={
                    fairnessReport.complianceStatus.euMDR
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }
                >
                  {fairnessReport.complianceStatus.euMDR ? 'Compliant' : 'Non-Compliant'}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="font-medium">HIPAA Compliance</span>
                <Badge className="bg-green-100 text-green-800">
                  {fairnessReport.complianceStatus.hipaa ? 'Compliant' : 'Non-Compliant'}
                </Badge>
              </div>
              {fairnessReport.complianceStatus.details.length > 0 && (
                <div className="mt-4 p-3 bg-gray-50 rounded">
                  <p className="text-sm font-medium mb-2">Details:</p>
                  <ul className="text-sm space-y-1">
                    {fairnessReport.complianceStatus.details.map((detail, index) => (
                      <li key={index}>• {detail}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

// Helper functions for mock data generation
function generateMockTestData(): RetinaImageWithDemographics[] {
  const demographics = [
    { race: 'White', ethnicity: 'Non-Hispanic', gender: 'male' as const, age: 55 },
    { race: 'Black', ethnicity: 'Non-Hispanic', gender: 'female' as const, age: 48 },
    { race: 'Asian', ethnicity: 'Non-Hispanic', gender: 'male' as const, age: 62 },
    { race: 'Hispanic', ethnicity: 'Hispanic', gender: 'female' as const, age: 51 },
    { race: 'South Asian', ethnicity: 'Indian', gender: 'male' as const, age: 45 },
  ];

  return Array.from({ length: 100 }, (_, i) => ({
    id: `img-${i}`,
    imageUrl: `https://example.com/image-${i}.jpg`,
    label: Math.random() > 0.7 ? Math.floor(Math.random() * 5) : 0,
    demographics: demographics[i % demographics.length],
  }));
}

function generateMockDemographicGroups(): DemographicGroup[] {
  return [
    {
      race: ['White'],
      ethnicity: ['Non-Hispanic'],
      gender: ['male', 'female'],
      ageRanges: ['40-50', '50-60', '60+'],
      geographicRegions: ['North America'],
      socioeconomicStatus: ['middle', 'high'],
    },
    {
      race: ['Black'],
      ethnicity: ['Non-Hispanic'],
      gender: ['male', 'female'],
      ageRanges: ['40-50', '50-60', '60+'],
      geographicRegions: ['North America'],
      socioeconomicStatus: ['low', 'middle'],
    },
    {
      race: ['Asian'],
      ethnicity: ['Non-Hispanic'],
      gender: ['male', 'female'],
      ageRanges: ['40-50', '50-60', '60+'],
      geographicRegions: ['North America', 'Asia'],
      socioeconomicStatus: ['middle', 'high'],
    },
    {
      race: ['Hispanic'],
      ethnicity: ['Hispanic'],
      gender: ['male', 'female'],
      ageRanges: ['40-50', '50-60', '60+'],
      geographicRegions: ['North America'],
      socioeconomicStatus: ['low', 'middle'],
    },
    {
      race: ['South Asian'],
      ethnicity: ['Indian'],
      gender: ['male', 'female'],
      ageRanges: ['40-50', '50-60'],
      geographicRegions: ['South Asia'],
      socioeconomicStatus: ['low', 'middle', 'high'],
    },
  ];
}
