/**
 * Comprehensive Bias and Fairness Types for RetinaScan AI
 * Ensures equitable performance across all patient demographics
 */

export interface DemographicGroup {
  race: string[];
  ethnicity: string[];
  gender: ('male' | 'female' | 'other')[];
  ageRanges: string[];
  geographicRegions: string[];
  socioeconomicStatus: ('low' | 'middle' | 'high')[];
}

export interface DemographicData {
  race?: string;
  ethnicity?: string;
  gender?: 'male' | 'female' | 'other';
  age?: number;
  geographicRegion?: string;
  socioeconomicStatus?: 'low' | 'middle' | 'high';
}

export interface FairnessMetrics {
  demographicParity: number;
  equalizedOdds: number;
  predictiveParity: number;
  falsePositiveRate: number;
  falseNegativeRate: number;
  truePositiveRate: number;
  trueNegativeRate: number;
  accuracy: number;
  sensitivity: number;
  specificity: number;
}

export interface BiasAuditResult {
  timestamp: string;
  modelVersion: string;
  overallMetrics: FairnessMetrics;
  subgroupMetrics: Record<string, FairnessMetrics>;
  biasFlags: BiasFlag[];
  recommendations: string[];
  auditId: string;
}

export interface BiasFlag {
  severity: 'low' | 'medium' | 'high';
  metric: string;
  subgroup: string;
  value: number;
  threshold: number;
  description: string;
  mitigationActions?: string[];
}

export interface FairnessConstraint {
  type: 'demographic_parity' | 'equalized_odds' | 'predictive_parity' | 'equal_opportunity';
  threshold: number;
  protectedAttributes: string[];
}

export interface DatasetInfo {
  name: string;
  source: string;
  demographics: DemographicGroup;
  totalSamples: number;
  representation: Record<string, number>;
}

export interface DemographicStats {
  totalSamples: number;
  raceDistribution: Record<string, number>;
  ethnicityDistribution: Record<string, number>;
  genderDistribution: Record<string, number>;
  ageDistribution: Record<string, number>;
  geographicDistribution: Record<string, number>;
}

export interface FairnessReport {
  executiveSummary: string;
  detailedAnalysis: string;
  demographicBreakdown: Record<string, FairnessMetrics>;
  biasMitigationHistory: BiasMitigationAction[];
  recommendations: string[];
  complianceStatus: ComplianceStatus;
  overallFairnessScore: number;
}

export interface BiasMitigationAction {
  timestamp: string;
  action: string;
  targetSubgroup: string;
  impact: 'positive' | 'neutral' | 'negative';
  details: string;
}

export interface ComplianceStatus {
  fda: boolean;
  euMDR: boolean;
  hipaa: boolean;
  details: string[];
}

export interface RetinaImageWithDemographics {
  id: string;
  imageUrl: string;
  label: number;
  demographics: DemographicData;
  metadata?: Record<string, any>;
}

export interface FairnessThresholds {
  demographicParity: number;
  equalizedOdds: number;
  falsePositiveParity: number;
  falseNegativeParity: number;
  accuracyDisparity: number;
}
