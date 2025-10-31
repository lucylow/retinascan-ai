/**
 * Bias Mitigation Strategies
 * Implements various techniques to reduce bias in model predictions
 */

import {
  RetinaImageWithDemographics,
  FairnessConstraint,
} from '../types/fairness';

export class BiasMitigationStrategies {
  /**
   * Apply reweighting based on demographic representation
   */
  static applyReweighting(
    trainingData: RetinaImageWithDemographics[],
    _labels: number[]
  ): { weights: number[]; augmentedData: RetinaImageWithDemographics[] } {
    const demographicGroups = this.groupByDemographics(trainingData);
    const groupWeights = this.calculateGroupWeights(demographicGroups);

    const weights = trainingData.map((image) => {
      const groupKey = this.getDemographicGroupKey(image);
      return groupWeights[groupKey] || 1.0;
    });

    return { weights, augmentedData: trainingData };
  }

  /**
   * Apply oversampling for underrepresented groups
   */
  static applyOversampling(
    trainingData: RetinaImageWithDemographics[]
  ): RetinaImageWithDemographics[] {
    const groups = this.groupByDemographics(trainingData);
    const maxGroupSize = Math.max(
      ...Object.values(groups).map((g) => g.length)
    );

    const augmentedData: RetinaImageWithDemographics[] = [];

    Object.entries(groups).forEach(([_group, images]) => {
      const currentSize = images.length;
      const oversampleFactor = Math.ceil(maxGroupSize / currentSize);

      for (let i = 0; i < oversampleFactor; i++) {
        augmentedData.push(...images);

        // Apply data augmentation to oversampled data
        if (i > 0) {
          const augmented = this.augmentImages(images);
          augmentedData.push(...augmented);
        }
      }
    });

    return augmentedData;
  }

  /**
   * Group images by demographics
   */
  private static groupByDemographics(
    data: RetinaImageWithDemographics[]
  ): Record<string, RetinaImageWithDemographics[]> {
    const groups: Record<string, RetinaImageWithDemographics[]> = {};

    data.forEach((image) => {
      const key = this.getDemographicGroupKey(image);
      if (!groups[key]) {
        groups[key] = [];
      }
      groups[key].push(image);
    });

    return groups;
  }

  /**
   * Calculate weights for each demographic group
   */
  private static calculateGroupWeights(
    groups: Record<string, RetinaImageWithDemographics[]>
  ): Record<string, number> {
    const totalImages = Object.values(groups).reduce(
      (sum, group) => sum + group.length,
      0
    );
    const numGroups = Object.keys(groups).length;
    const averageSize = totalImages / numGroups;

    const weights: Record<string, number> = {};

    Object.entries(groups).forEach(([group, images]) => {
      if (images.length > 0) {
        weights[group] = averageSize / images.length;
      }
    });

    return weights;
  }

  /**
   * Get demographic group key
   */
  private static getDemographicGroupKey(
    image: RetinaImageWithDemographics
  ): string {
    const demo = image.demographics;
    const ageRange = demo.age ? this.getAgeRange(demo.age) : 'unknown';
    return `${demo.race || 'unknown'}-${demo.ethnicity || 'unknown'}-${
      demo.gender || 'unknown'
    }-${ageRange}`;
  }

  /**
   * Get age range from age
   */
  private static getAgeRange(age: number): string {
    if (age < 30) return '20-30';
    if (age < 40) return '30-40';
    if (age < 50) return '40-50';
    if (age < 60) return '50-60';
    return '60+';
  }

  /**
   * Augment images for oversampling
   */
  private static augmentImages(
    images: RetinaImageWithDemographics[]
  ): RetinaImageWithDemographics[] {
    // In production, this would apply actual image augmentation
    // For now, return copies with augmented metadata
    return images.map((image, index) => ({
      ...image,
      id: `${image.id}-aug-${index}`,
      metadata: {
        ...image.metadata,
        augmented: true,
        augmentationType: this.selectAugmentationType(),
      },
    }));
  }

  /**
   * Select random augmentation type
   */
  private static selectAugmentationType(): string {
    const types = [
      'rotation',
      'flip',
      'brightness',
      'contrast',
      'zoom',
      'translation',
    ];
    return types[Math.floor(Math.random() * types.length)];
  }

  /**
   * Create fairness-regularized loss function
   */
  static createFairnessRegularizedLoss(constraints: FairnessConstraint[]) {
    return class FairnessLoss {
      static calculateLoss(
        predictions: number[],
        labels: number[],
        demographics: any[]
      ): number {
        const baseLoss = this.calculateBaseLoss(predictions, labels);
        const fairnessPenalty = this.calculateFairnessPenalty(
          predictions,
          labels,
          demographics,
          constraints
        );

        return baseLoss + fairnessPenalty;
      }

      static calculateBaseLoss(
        predictions: number[],
        labels: number[]
      ): number {
        // Binary cross-entropy loss
        let loss = 0;
        for (let i = 0; i < predictions.length; i++) {
          const pred = Math.max(0.0001, Math.min(0.9999, predictions[i]));
          const label = labels[i];
          loss -=
            label * Math.log(pred) + (1 - label) * Math.log(1 - pred);
        }
        return loss / predictions.length;
      }

      static calculateFairnessPenalty(
        predictions: number[],
        labels: number[],
        demographics: any[],
        constraints: FairnessConstraint[]
      ): number {
        let penalty = 0;

        constraints.forEach((constraint) => {
          switch (constraint.type) {
            case 'demographic_parity':
              penalty += this.demographicParityPenalty(
                predictions,
                demographics
              );
              break;
            case 'equalized_odds':
              penalty += this.equalizedOddsPenalty(
                predictions,
                labels,
                demographics
              );
              break;
            case 'predictive_parity':
              penalty += this.predictiveParityPenalty(
                predictions,
                labels,
                demographics
              );
              break;
            case 'equal_opportunity':
              penalty += this.equalOpportunityPenalty(
                predictions,
                labels,
                demographics
              );
              break;
          }
        });

        return penalty;
      }

      static demographicParityPenalty(
        predictions: number[],
        demographics: any[]
      ): number {
        // Penalize differences in positive prediction rates across groups
        const groups = this.groupPredictionsByDemographic(
          predictions,
          demographics
        );
        const groupRates = Object.values(groups).map(
          (groupPreds) =>
            groupPreds.filter((p) => p > 0.5).length / groupPreds.length
        );

        if (groupRates.length < 2) return 0;

        const meanRate =
          groupRates.reduce((a, b) => a + b, 0) / groupRates.length;
        const variance = groupRates.reduce(
          (sum, rate) => sum + Math.pow(rate - meanRate, 2),
          0
        ) / groupRates.length;

        return variance; // Penalize variance in prediction rates
      }

      static equalizedOddsPenalty(
        predictions: number[],
        labels: number[],
        demographics: any[]
      ): number {
        // Penalize differences in TPR and FPR across groups
        const groups = this.groupPredictionsByDemographic(
          predictions,
          demographics
        );
        let penalty = 0;

        Object.values(groups).forEach((groupPreds, groupIndex) => {
          const groupLabels = labels.slice(
            groupIndex * groupPreds.length,
            (groupIndex + 1) * groupPreds.length
          );
          const tpr = this.calculateTPR(groupPreds, groupLabels);
          const fpr = this.calculateFPR(groupPreds, groupLabels);

          // Compare with other groups
          Object.values(groups).forEach((otherPreds, otherIndex) => {
            if (groupIndex === otherIndex) return;
            const otherLabels = labels.slice(
              otherIndex * otherPreds.length,
              (otherIndex + 1) * otherPreds.length
            );
            const otherTPR = this.calculateTPR(otherPreds, otherLabels);
            const otherFPR = this.calculateFPR(otherPreds, otherLabels);

            penalty += Math.abs(tpr - otherTPR) + Math.abs(fpr - otherFPR);
          });
        });

        return penalty;
      }

      static predictiveParityPenalty(
        predictions: number[],
        labels: number[],
        demographics: any[]
      ): number {
        // Penalize differences in PPV across groups
        const groups = this.groupPredictionsByDemographic(
          predictions,
          demographics
        );
        let penalty = 0;

        Object.values(groups).forEach((groupPreds, groupIndex) => {
          const groupLabels = labels.slice(
            groupIndex * groupPreds.length,
            (groupIndex + 1) * groupPreds.length
          );
          const ppv = this.calculatePPV(groupPreds, groupLabels);

          // Compare with other groups
          Object.values(groups).forEach((otherPreds, otherIndex) => {
            if (groupIndex === otherIndex) return;
            const otherLabels = labels.slice(
              otherIndex * otherPreds.length,
              (otherIndex + 1) * otherPreds.length
            );
            const otherPPV = this.calculatePPV(otherPreds, otherLabels);

            penalty += Math.abs(ppv - otherPPV);
          });
        });

        return penalty;
      }

      static equalOpportunityPenalty(
        predictions: number[],
        labels: number[],
        demographics: any[]
      ): number {
        // Penalize differences in TPR (equal opportunity)
        return this.equalizedOddsPenalty(predictions, labels, demographics);
      }

      static groupPredictionsByDemographic(
        predictions: number[],
        demographics: any[]
      ): Record<string, number[]> {
        const groups: Record<string, number[]> = {};

        predictions.forEach((pred, index) => {
          const demo = demographics[index];
          const key = `${demo.race || 'unknown'}-${demo.gender || 'unknown'}`;
          if (!groups[key]) {
            groups[key] = [];
          }
          groups[key].push(pred);
        });

        return groups;
      }

      static calculateTPR(predictions: number[], labels: number[]): number {
        let tp = 0;
        let fn = 0;
        predictions.forEach((pred, i) => {
          if (labels[i] === 1 && pred > 0.5) tp++;
          if (labels[i] === 1 && pred <= 0.5) fn++;
        });
        return tp + fn > 0 ? tp / (tp + fn) : 0;
      }

      static calculateFPR(predictions: number[], labels: number[]): number {
        let fp = 0;
        let tn = 0;
        predictions.forEach((pred, i) => {
          if (labels[i] === 0 && pred > 0.5) fp++;
          if (labels[i] === 0 && pred <= 0.5) tn++;
        });
        return fp + tn > 0 ? fp / (fp + tn) : 0;
      }

      static calculatePPV(predictions: number[], labels: number[]): number {
        let tp = 0;
        let fp = 0;
        predictions.forEach((pred, i) => {
          if (pred > 0.5 && labels[i] === 1) tp++;
          if (pred > 0.5 && labels[i] === 0) fp++;
        });
        return tp + fp > 0 ? tp / (tp + fp) : 0;
      }
    };
  }
}
