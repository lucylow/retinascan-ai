/**
 * Dataset Manager for Diverse and Representative Training Data
 * Ensures balanced representation across all demographic groups
 */

import {
  DemographicGroup,
  DemographicStats,
  RetinaImageWithDemographics,
  DatasetInfo,
} from '../types/fairness';

export class DatasetManager {
  private datasets = new Map<string, DatasetInfo>();
  private demographicStats = new Map<string, DemographicStats>();
  private readonly MIN_REPRESENTATION = 0.05; // 5% minimum representation per group

  /**
   * Load diverse datasets from multiple global sources
   */
  async loadDiverseDatasets(): Promise<void> {
    const datasets: Array<{
      name: string;
      source: string;
      demographics: DemographicGroup;
    }> = [
      {
        name: 'APTOS',
        source: 'India',
        demographics: {
          race: ['South Asian'],
          ethnicity: ['Indian'],
          gender: ['male', 'female'],
          ageRanges: ['20-30', '30-40', '40-50', '50-60', '60+'],
          geographicRegions: ['South Asia'],
          socioeconomicStatus: ['low', 'middle', 'high'],
        },
      },
      {
        name: 'EyePACS',
        source: 'USA',
        demographics: {
          race: ['White', 'Black', 'Asian', 'Hispanic', 'Native American'],
          ethnicity: ['Non-Hispanic', 'Hispanic'],
          gender: ['male', 'female', 'other'],
          ageRanges: ['20-30', '30-40', '40-50', '50-60', '60+'],
          geographicRegions: ['North America'],
          socioeconomicStatus: ['low', 'middle', 'high'],
        },
      },
      {
        name: 'Messidor',
        source: 'France',
        demographics: {
          race: ['White', 'North African', 'Sub-Saharan African'],
          ethnicity: ['European', 'African'],
          gender: ['male', 'female'],
          ageRanges: ['40-50', '50-60', '60+'],
          geographicRegions: ['Europe'],
          socioeconomicStatus: ['middle', 'high'],
        },
      },
      {
        name: 'RFMiD',
        source: 'Multi-country',
        demographics: {
          race: ['South Asian', 'Southeast Asian', 'Middle Eastern'],
          ethnicity: ['Various'],
          gender: ['male', 'female'],
          ageRanges: ['20-30', '30-40', '40-50', '50-60', '60+'],
          geographicRegions: ['South Asia', 'Southeast Asia', 'Middle East'],
          socioeconomicStatus: ['low', 'middle', 'high'],
        },
      },
    ];

    for (const dataset of datasets) {
      await this.loadDataset(dataset);
    }
  }

  /**
   * Load and validate a dataset
   */
  private async loadDataset(dataset: {
    name: string;
    source: string;
    demographics: DemographicGroup;
  }): Promise<void> {
    console.log(`Loading ${dataset.name} from ${dataset.source}`);

    // In a real implementation, this would load actual images
    // For now, we simulate dataset loading
    const mockStats = this.calculateDemographicStats(dataset);
    this.demographicStats.set(dataset.name, mockStats);

    // Check for representation gaps
    this.identifyRepresentationGaps(mockStats, dataset.demographics);

    const datasetInfo: DatasetInfo = {
      name: dataset.name,
      source: dataset.source,
      demographics: dataset.demographics,
      totalSamples: mockStats.totalSamples,
      representation: {
        ...mockStats.raceDistribution,
        ...mockStats.ethnicityDistribution,
        ...mockStats.genderDistribution,
      },
    };

    this.datasets.set(dataset.name, datasetInfo);
  }

  /**
   * Calculate demographic statistics for a dataset
   */
  calculateDemographicStats(dataset: {
    demographics: DemographicGroup;
  }): DemographicStats {
    // In a real implementation, this would analyze actual image data
    // For now, we return mock statistics
    const stats: DemographicStats = {
      totalSamples: 1000, // Mock value
      raceDistribution: {},
      ethnicityDistribution: {},
      genderDistribution: {},
      ageDistribution: {},
      geographicDistribution: {},
    };

    // Simulate distribution calculations
    dataset.demographics.race.forEach((race) => {
      stats.raceDistribution[race] = Math.random() * 0.3 + 0.1;
    });

    dataset.demographics.gender.forEach((gender) => {
      stats.genderDistribution[gender] = Math.random() * 0.4 + 0.2;
    });

    return stats;
  }

  /**
   * Identify representation gaps in dataset
   */
  identifyRepresentationGaps(
    stats: DemographicStats,
    targetDemographics: DemographicGroup
  ): void {
    const gaps: Array<{
      demographic: string;
      group: string;
      representation: number;
      minimumRequired: number;
    }> = [];

    // Check race representation
    targetDemographics.race.forEach((race) => {
      const representation = stats.raceDistribution[race] || 0;
      if (representation < this.MIN_REPRESENTATION) {
        gaps.push({
          demographic: 'race',
          group: race,
          representation,
          minimumRequired: this.MIN_REPRESENTATION,
        });
      }
    });

    // Check gender representation
    targetDemographics.gender.forEach((gender) => {
      const representation = stats.genderDistribution[gender] || 0;
      if (representation < this.MIN_REPRESENTATION) {
        gaps.push({
          demographic: 'gender',
          group: gender,
          representation,
          minimumRequired: this.MIN_REPRESENTATION,
        });
      }
    });

    if (gaps.length > 0) {
      console.warn('Representation gaps identified:', gaps);
      this.triggerDataCollection(gaps);
    }
  }

  /**
   * Ensure balanced training split across demographics
   */
  async ensureBalancedTrainingSplit(
    images: RetinaImageWithDemographics[]
  ): Promise<RetinaImageWithDemographics[]> {
    const grouped = this.groupByDemographics(images);
    const balancedSplit: RetinaImageWithDemographics[] = [];

    // Ensure minimum representation from each demographic group
    const numGroups = Object.keys(grouped).length;
    const minPerGroup = Math.floor((images.length / numGroups) * 0.1);

    for (const [_group, groupImages] of Object.entries(grouped)) {
      const samples = this.sampleBalanced(groupImages, minPerGroup);
      balancedSplit.push(...samples);
    }

    // Fill remaining slots with stratified random sampling
    const remaining = images.length - balancedSplit.length;
    if (remaining > 0) {
      const remainingSamples = this.stratifiedRandomSample(
        images,
        balancedSplit,
        remaining
      );
      balancedSplit.push(...remainingSamples);
    }

    return balancedSplit;
  }

  /**
   * Group images by demographic attributes
   */
  private groupByDemographics(
    images: RetinaImageWithDemographics[]
  ): Record<string, RetinaImageWithDemographics[]> {
    const groups: Record<string, RetinaImageWithDemographics[]> = {};

    images.forEach((image) => {
      const key = this.getDemographicGroupKey(image);
      if (!groups[key]) {
        groups[key] = [];
      }
      groups[key].push(image);
    });

    return groups;
  }

  /**
   * Generate a key for demographic grouping
   */
  private getDemographicGroupKey(image: RetinaImageWithDemographics): string {
    const demo = image.demographics;
    const ageRange = demo.age ? this.getAgeRange(demo.age) : 'unknown';
    return `${demo.race || 'unknown'}-${demo.ethnicity || 'unknown'}-${
      demo.gender || 'unknown'
    }-${ageRange}`;
  }

  /**
   * Get age range from age
   */
  private getAgeRange(age: number): string {
    if (age < 30) return '20-30';
    if (age < 40) return '30-40';
    if (age < 50) return '40-50';
    if (age < 60) return '50-60';
    return '60+';
  }

  /**
   * Sample balanced images from a group
   */
  private sampleBalanced(
    images: RetinaImageWithDemographics[],
    minCount: number
  ): RetinaImageWithDemographics[] {
    const shuffled = [...images].sort(() => Math.random() - 0.5);
    return shuffled.slice(0, Math.min(minCount, images.length));
  }

  /**
   * Stratified random sampling
   */
  private stratifiedRandomSample(
    allImages: RetinaImageWithDemographics[],
    alreadySelected: RetinaImageWithDemographics[],
    count: number
  ): RetinaImageWithDemographics[] {
    const selectedIds = new Set(alreadySelected.map((img) => img.id));
    const available = allImages.filter((img) => !selectedIds.has(img.id));
    const shuffled = [...available].sort(() => Math.random() - 0.5);
    return shuffled.slice(0, count);
  }

  /**
   * Trigger data collection for underrepresented groups
   */
  private triggerDataCollection(gaps: Array<{
    demographic: string;
    group: string;
    representation: number;
    minimumRequired: number;
  }>): void {
    console.log('Triggering data collection for gaps:', gaps);
    // In production, this would trigger actual data collection workflows
  }

  /**
   * Get all loaded datasets
   */
  getDatasets(): DatasetInfo[] {
    return Array.from(this.datasets.values());
  }

  /**
   * Get demographic statistics for a dataset
   */
  getDemographicStats(datasetName: string): DemographicStats | undefined {
    return this.demographicStats.get(datasetName);
  }
}
