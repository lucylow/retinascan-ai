/**
 * Fairness Auditor for Continuous Bias Monitoring and Subgroup Analysis
 * Conducts regular audits to ensure equitable performance across demographics
 */

import {
  FairnessMetrics,
  BiasAuditResult,
  BiasFlag,
  DemographicGroup,
  RetinaImageWithDemographics,
  FairnessThresholds,
} from '../types/fairness';

export class FairnessAuditor {
  private auditHistory: BiasAuditResult[] = [];
  private fairnessThresholds: FairnessThresholds = {
    demographicParity: 0.8,
    equalizedOdds: 0.85,
    falsePositiveParity: 0.8,
    falseNegativeParity: 0.8,
    accuracyDisparity: 0.15,
  };

  /**
   * Perform comprehensive fairness audit
   */
  async performComprehensiveAudit(
    predictions: Array<{ imageId: string; predictedLabel: number; confidence: number }>,
    testData: RetinaImageWithDemographics[],
    demographicGroups: DemographicGroup[]
  ): Promise<BiasAuditResult> {
    const overallMetrics = this.calculateOverallMetrics(predictions, testData);
    const subgroupMetrics: Record<string, FairnessMetrics> = {};
    const biasFlags: BiasFlag[] = [];

    // Analyze each demographic subgroup
    for (const group of demographicGroups) {
      const subgroupData = this.filterByDemographics(testData, group);
      if (subgroupData.length === 0) continue;

      const subgroupPredictions = predictions.filter((pred) =>
        subgroupData.some((data) => data.id === pred.imageId)
      );

      const metrics = this.calculateSubgroupMetrics(
        subgroupPredictions,
        subgroupData
      );
      const groupKey = this.getGroupKey(group);
      subgroupMetrics[groupKey] = metrics;

      // Check for bias flags
      const flags = this.detectBiasFlags(metrics, group);
      biasFlags.push(...flags);
    }

    // Generate recommendations
    const recommendations = this.generateRecommendations({
      overallMetrics,
      subgroupMetrics,
      biasFlags,
    });

    const auditResult: BiasAuditResult = {
      timestamp: new Date().toISOString(),
      modelVersion: '1.0.0', // In production, get from actual model
      overallMetrics,
      subgroupMetrics,
      biasFlags,
      recommendations,
      auditId: `audit-${Date.now()}`,
    };

    this.auditHistory.push(auditResult);
    return auditResult;
  }

  /**
   * Calculate overall fairness metrics
   */
  private calculateOverallMetrics(
    predictions: Array<{ imageId: string; predictedLabel: number; confidence: number }>,
    testData: RetinaImageWithDemographics[]
  ): FairnessMetrics {
    const truePositives = this.calculateTruePositives(predictions, testData);
    const trueNegatives = this.calculateTrueNegatives(predictions, testData);
    const falsePositives = this.calculateFalsePositives(predictions, testData);
    const falseNegatives = this.calculateFalseNegatives(predictions, testData);

    const total = testData.length;
    const positivePredictions = truePositives + falsePositives;
    const actualPositives = truePositives + falseNegatives;
    const actualNegatives = trueNegatives + falsePositives;

    return {
      demographicParity: positivePredictions / total,
      equalizedOdds: this.calculateEqualizedOdds(
        truePositives,
        falsePositives,
        actualPositives,
        actualNegatives
      ),
      predictiveParity:
        actualPositives > 0 ? truePositives / actualPositives : 0,
      falsePositiveRate: actualNegatives > 0 ? falsePositives / actualNegatives : 0,
      falseNegativeRate: actualPositives > 0 ? falseNegatives / actualPositives : 0,
      truePositiveRate: actualPositives > 0 ? truePositives / actualPositives : 0,
      trueNegativeRate: actualNegatives > 0 ? trueNegatives / actualNegatives : 0,
      accuracy: total > 0 ? (truePositives + trueNegatives) / total : 0,
      sensitivity: actualPositives > 0 ? truePositives / actualPositives : 0,
      specificity: actualNegatives > 0 ? trueNegatives / actualNegatives : 0,
    };
  }

  /**
   * Calculate subgroup-specific metrics
   */
  private calculateSubgroupMetrics(
    predictions: Array<{ imageId: string; predictedLabel: number; confidence: number }>,
    subgroupData: RetinaImageWithDemographics[]
  ): FairnessMetrics {
    const truePositives = this.calculateTruePositives(predictions, subgroupData);
    const trueNegatives = this.calculateTrueNegatives(predictions, subgroupData);
    const falsePositives = this.calculateFalsePositives(predictions, subgroupData);
    const falseNegatives = this.calculateFalseNegatives(predictions, subgroupData);

    const total = subgroupData.length;
    const positivePredictions = truePositives + falsePositives;
    const actualPositives = truePositives + falseNegatives;
    const actualNegatives = trueNegatives + falsePositives;

    return {
      demographicParity: total > 0 ? positivePredictions / total : 0,
      equalizedOdds: this.calculateEqualizedOdds(
        truePositives,
        falsePositives,
        actualPositives,
        actualNegatives
      ),
      predictiveParity:
        actualPositives > 0 ? truePositives / actualPositives : 0,
      falsePositiveRate: actualNegatives > 0 ? falsePositives / actualNegatives : 0,
      falseNegativeRate: actualPositives > 0 ? falseNegatives / actualPositives : 0,
      truePositiveRate: actualPositives > 0 ? truePositives / actualPositives : 0,
      trueNegativeRate: actualNegatives > 0 ? trueNegatives / actualNegatives : 0,
      accuracy: total > 0 ? (truePositives + trueNegatives) / total : 0,
      sensitivity: actualPositives > 0 ? truePositives / actualPositives : 0,
      specificity: actualNegatives > 0 ? trueNegatives / actualNegatives : 0,
    };
  }

  /**
   * Calculate true positives (DR detected correctly)
   */
  private calculateTruePositives(
    predictions: Array<{ imageId: string; predictedLabel: number }>,
    data: RetinaImageWithDemographics[]
  ): number {
    return predictions.filter((pred) => {
      const image = data.find((img) => img.id === pred.imageId);
      return image && pred.predictedLabel > 0 && image.label > 0;
    }).length;
  }

  /**
   * Calculate true negatives (No DR detected correctly)
   */
  private calculateTrueNegatives(
    predictions: Array<{ imageId: string; predictedLabel: number }>,
    data: RetinaImageWithDemographics[]
  ): number {
    return predictions.filter((pred) => {
      const image = data.find((img) => img.id === pred.imageId);
      return image && pred.predictedLabel === 0 && image.label === 0;
    }).length;
  }

  /**
   * Calculate false positives (DR predicted but not present)
   */
  private calculateFalsePositives(
    predictions: Array<{ imageId: string; predictedLabel: number }>,
    data: RetinaImageWithDemographics[]
  ): number {
    return predictions.filter((pred) => {
      const image = data.find((img) => img.id === pred.imageId);
      return image && pred.predictedLabel > 0 && image.label === 0;
    }).length;
  }

  /**
   * Calculate false negatives (DR missed)
   */
  private calculateFalseNegatives(
    predictions: Array<{ imageId: string; predictedLabel: number }>,
    data: RetinaImageWithDemographics[]
  ): number {
    return predictions.filter((pred) => {
      const image = data.find((img) => img.id === pred.imageId);
      return image && pred.predictedLabel === 0 && image.label > 0;
    }).length;
  }

  /**
   * Calculate equalized odds score
   */
  private calculateEqualizedOdds(
    truePositives: number,
    falsePositives: number,
    actualPositives: number,
    actualNegatives: number
  ): number {
    const tpr = actualPositives > 0 ? truePositives / actualPositives : 0;
    const fpr = actualNegatives > 0 ? falsePositives / actualNegatives : 0;
    // Equalized odds: TPR and FPR should be similar across groups
    // Score is based on how balanced they are (1.0 = perfectly balanced)
    return 1 - Math.abs(tpr - fpr);
  }

  /**
   * Detect bias flags for a subgroup
   */
  private detectBiasFlags(
    metrics: FairnessMetrics,
    group: DemographicGroup
  ): BiasFlag[] {
    const flags: BiasFlag[] = [];
    const groupKey = this.getGroupKey(group);

    // Check demographic parity
    if (metrics.demographicParity < this.fairnessThresholds.demographicParity) {
      flags.push({
        severity: 'high',
        metric: 'demographicParity',
        subgroup: groupKey,
        value: metrics.demographicParity,
        threshold: this.fairnessThresholds.demographicParity,
        description: `Model shows significant demographic parity bias for ${groupKey}`,
        mitigationActions: [
          'Retrain with balanced dataset',
          'Apply reweighting techniques',
          'Implement oversampling for underrepresented groups',
        ],
      });
    }

    // Check equalized odds
    if (metrics.equalizedOdds < this.fairnessThresholds.equalizedOdds) {
      flags.push({
        severity: 'medium',
        metric: 'equalizedOdds',
        subgroup: groupKey,
        value: metrics.equalizedOdds,
        threshold: this.fairnessThresholds.equalizedOdds,
        description: `Model shows unequal true positive rates across groups`,
        mitigationActions: [
          'Implement adversarial debiasing',
          'Adjust decision thresholds per subgroup',
        ],
      });
    }

    // Check false positive rate parity
    if (metrics.falsePositiveRate > this.fairnessThresholds.falsePositiveParity) {
      flags.push({
        severity: 'high',
        metric: 'falsePositiveRate',
        subgroup: groupKey,
        value: metrics.falsePositiveRate,
        threshold: this.fairnessThresholds.falsePositiveParity,
        description: `High false positive rate for ${groupKey} may lead to over-referral`,
        mitigationActions: [
          'Adjust classification threshold',
          'Improve feature extraction for this subgroup',
          'Collect more training data',
        ],
      });
    }

    // Check false negative rate parity
    if (metrics.falseNegativeRate > this.fairnessThresholds.falseNegativeParity) {
      flags.push({
        severity: 'high',
        metric: 'falseNegativeRate',
        subgroup: groupKey,
        value: metrics.falseNegativeRate,
        threshold: this.fairnessThresholds.falseNegativeParity,
        description: `High false negative rate for ${groupKey} may lead to missed diagnoses`,
        mitigationActions: [
          'Lower classification threshold for this subgroup',
          'Enhance sensitivity-focused training',
          'Add more severe DR cases to training',
        ],
      });
    }

    return flags;
  }

  /**
   * Generate recommendations based on audit results
   */
  private generateRecommendations(auditData: {
    overallMetrics: FairnessMetrics;
    subgroupMetrics: Record<string, FairnessMetrics>;
    biasFlags: BiasFlag[];
  }): string[] {
    const recommendations: string[] = [];

    // Analyze bias flags and generate specific recommendations
    const highSeverityFlags = auditData.biasFlags.filter(
      (flag) => flag.severity === 'high'
    );

    if (highSeverityFlags.length > 0) {
      recommendations.push(
        'Immediate model retraining required with focus on underrepresented groups'
      );
      recommendations.push(
        'Consider collecting additional data for affected demographic groups'
      );
    }

    // Check for systematic biases
    const racialBiases = auditData.biasFlags.filter(
      (flag) =>
        flag.subgroup.includes('race') || flag.subgroup.includes('ethnicity')
    );

    if (racialBiases.length > 2) {
      recommendations.push(
        'Implement racial bias mitigation techniques: adversarial debiasing and reweighting'
      );
      recommendations.push(
        'Engage with diverse clinical partners for dataset validation'
      );
    }

    // Performance disparity recommendations
    const accuracyDisparities = this.calculateAccuracyDisparities(
      auditData.subgroupMetrics
    );
    if (accuracyDisparities > this.fairnessThresholds.accuracyDisparity) {
      recommendations.push(
        'Significant accuracy disparities detected. Implement subgroup-specific calibration'
      );
      recommendations.push(
        'Consider ensemble approaches with group-specific models'
      );
    }

    // Add recommendations based on specific metrics
    if (auditData.overallMetrics.falseNegativeRate > 0.2) {
      recommendations.push(
        'Overall false negative rate is high. Adjust sensitivity thresholds'
      );
    }

    if (auditData.overallMetrics.falsePositiveRate > 0.3) {
      recommendations.push(
        'Overall false positive rate is high. Consider stricter specificity requirements'
      );
    }

    return recommendations;
  }

  /**
   * Calculate accuracy disparities across subgroups
   */
  private calculateAccuracyDisparities(
    subgroupMetrics: Record<string, FairnessMetrics>
  ): number {
    const accuracies = Object.values(subgroupMetrics).map((m) => m.accuracy);
    if (accuracies.length === 0) return 0;
    const max = Math.max(...accuracies);
    const min = Math.min(...accuracies);
    return max - min;
  }

  /**
   * Filter data by demographic group
   */
  private filterByDemographics(
    data: RetinaImageWithDemographics[],
    group: DemographicGroup
  ): RetinaImageWithDemographics[] {
    return data.filter((image) => {
      const demo = image.demographics;
      const raceMatch =
        !demo.race || group.race.length === 0 || group.race.includes(demo.race);
      const ethnicityMatch =
        !demo.ethnicity ||
        group.ethnicity.length === 0 ||
        group.ethnicity.includes(demo.ethnicity);
      const genderMatch =
        !demo.gender ||
        group.gender.length === 0 ||
        group.gender.includes(demo.gender);

      return raceMatch && ethnicityMatch && genderMatch;
    });
  }

  /**
   * Generate group key for identification
   */
  private getGroupKey(group: DemographicGroup): string {
    return `${group.race.join('-')}_${group.ethnicity.join('-')}_${group.gender.join('-')}`;
  }

  /**
   * Start continuous monitoring
   */
  async continuousMonitoring(
    getModel: () => any,
    getProductionData: () => Promise<RetinaImageWithDemographics[]>,
    getDemographicGroups: () => Promise<DemographicGroup[]>
  ): Promise<void> {
    // In production, this would set up actual monitoring
    console.log('Starting continuous fairness monitoring...');
    
    setInterval(async () => {
      try {
        const model = getModel();
        const recentData = await getProductionData();
        const groups = await getDemographicGroups();

        // Generate predictions
        const predictions = await this.generatePredictions(model, recentData);

        // Perform audit
        const audit = await this.performComprehensiveAudit(
          predictions,
          recentData,
          groups
        );

        if (audit.biasFlags.length > 0) {
          await this.alertBiasDetected(audit);
        }

        // Log fairness metrics
        await this.logFairnessMetrics(audit);
      } catch (error) {
        console.error('Error in continuous monitoring:', error);
      }
    }, 24 * 60 * 60 * 1000); // Daily monitoring
  }

  /**
   * Generate predictions from model
   */
  private async generatePredictions(
    _model: any,
    data: RetinaImageWithDemographics[]
  ): Promise<Array<{ imageId: string; predictedLabel: number; confidence: number }>> {
    // In production, this would call the actual model
    // For now, return mock predictions
    return data.map((image) => ({
      imageId: image.id,
      predictedLabel: image.label, // Mock: assume perfect prediction
      confidence: 0.85,
    }));
  }

  /**
   * Alert when bias is detected
   */
  private async alertBiasDetected(audit: BiasAuditResult): Promise<void> {
    console.warn('Bias detected in audit:', audit.auditId);
    // In production, this would send alerts to monitoring systems
  }

  /**
   * Log fairness metrics
   */
  private async logFairnessMetrics(audit: BiasAuditResult): Promise<void> {
    console.log('Fairness metrics logged:', {
      auditId: audit.auditId,
      timestamp: audit.timestamp,
      overallAccuracy: audit.overallMetrics.accuracy,
      biasFlagsCount: audit.biasFlags.length,
    });
    // In production, this would log to monitoring systems
  }

  /**
   * Get audit history
   */
  getAuditHistory(): BiasAuditResult[] {
    return this.auditHistory;
  }

  /**
   * Get latest audit
   */
  getLatestAudit(): BiasAuditResult | null {
    return this.auditHistory.length > 0
      ? this.auditHistory[this.auditHistory.length - 1]
      : null;
  }
}
