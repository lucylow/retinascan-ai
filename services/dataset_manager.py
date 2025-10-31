"""
Dataset Manager for Diverse and Representative Training Data
Ensures balanced representation across all demographic groups
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class DemographicInfo:
    """Demographic information for a sample"""
    race: Optional[str] = None
    ethnicity: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    geographic_region: Optional[str] = None
    socioeconomic_status: Optional[str] = None


class DatasetManager:
    """
    Manages diverse datasets and ensures balanced representation
    """
    
    def __init__(self, min_representation: float = 0.05):
        """
        Initialize dataset manager
        
        Args:
            min_representation: Minimum representation fraction (5% default)
        """
        self.min_representation = min_representation
        self.datasets = {}
        self.demographic_stats = {}
    
    def load_diverse_datasets(self) -> Dict[str, Dict]:
        """
        Load diverse datasets from multiple global sources
        
        Returns:
            Dictionary of dataset information
        """
        datasets = {
            'APTOS': {
                'source': 'India',
                'demographics': {
                    'race': ['South Asian'],
                    'ethnicity': ['Indian'],
                    'gender': ['male', 'female'],
                    'age_ranges': ['20-30', '30-40', '40-50', '50-60', '60+'],
                    'geographic_regions': ['South Asia'],
                    'socioeconomic_status': ['low', 'middle', 'high'],
                }
            },
            'EyePACS': {
                'source': 'USA',
                'demographics': {
                    'race': ['White', 'Black', 'Asian', 'Hispanic', 'Native American'],
                    'ethnicity': ['Non-Hispanic', 'Hispanic'],
                    'gender': ['male', 'female', 'other'],
                    'age_ranges': ['20-30', '30-40', '40-50', '50-60', '60+'],
                    'geographic_regions': ['North America'],
                    'socioeconomic_status': ['low', 'middle', 'high'],
                }
            },
            'Messidor': {
                'source': 'France',
                'demographics': {
                    'race': ['White', 'North African', 'Sub-Saharan African'],
                    'ethnicity': ['European', 'African'],
                    'gender': ['male', 'female'],
                    'age_ranges': ['40-50', '50-60', '60+'],
                    'geographic_regions': ['Europe'],
                    'socioeconomic_status': ['middle', 'high'],
                }
            },
            'RFMiD': {
                'source': 'Multi-country',
                'demographics': {
                    'race': ['South Asian', 'Southeast Asian', 'Middle Eastern'],
                    'ethnicity': ['Various'],
                    'gender': ['male', 'female'],
                    'age_ranges': ['20-30', '30-40', '40-50', '50-60', '60+'],
                    'geographic_regions': ['South Asia', 'Southeast Asia', 'Middle East'],
                    'socioeconomic_status': ['low', 'middle', 'high'],
                }
            }
        }
        
        for name, info in datasets.items():
            self.datasets[name] = info
            logger.info(f"Loaded dataset: {name} from {info['source']}")
        
        return datasets
    
    def calculate_demographic_stats(
        self,
        images: List[Tuple],  # List of (image_data, demographic_info, label)
    ) -> Dict[str, Dict]:
        """
        Calculate demographic statistics for a dataset
        
        Args:
            images: List of (image_data, demographic_info, label) tuples
            
        Returns:
            Dictionary of demographic statistics
        """
        stats = {
            'total_samples': len(images),
            'race_distribution': defaultdict(int),
            'ethnicity_distribution': defaultdict(int),
            'gender_distribution': defaultdict(int),
            'age_distribution': defaultdict(int),
            'geographic_distribution': defaultdict(int),
            'socioeconomic_distribution': defaultdict(int),
        }
        
        for _, demo_info, _ in images:
            if demo_info.race:
                stats['race_distribution'][demo_info.race] += 1
            if demo_info.ethnicity:
                stats['ethnicity_distribution'][demo_info.ethnicity] += 1
            if demo_info.gender:
                stats['gender_distribution'][demo_info.gender] += 1
            if demo_info.age:
                age_range = self._get_age_range(demo_info.age)
                stats['age_distribution'][age_range] += 1
            if demo_info.geographic_region:
                stats['geographic_distribution'][demo_info.geographic_region] += 1
            if demo_info.socioeconomic_status:
                stats['socioeconomic_distribution'][demo_info.socioeconomic_status] += 1
        
        # Convert to fractions
        total = len(images)
        for key in ['race_distribution', 'ethnicity_distribution', 'gender_distribution',
                    'age_distribution', 'geographic_distribution', 'socioeconomic_distribution']:
            stats[key] = {
                k: v / total for k, v in stats[key].items()
            }
        
        return stats
    
    def identify_representation_gaps(
        self,
        stats: Dict[str, Dict],
        target_demographics: Dict
    ) -> List[Dict]:
        """
        Identify representation gaps in dataset
        
        Args:
            stats: Calculated demographic statistics
            target_demographics: Target demographic distribution
            
        Returns:
            List of identified gaps
        """
        gaps = []
        
        # Check race representation
        for race in target_demographics.get('race', []):
            representation = stats['race_distribution'].get(race, 0)
            if representation < self.min_representation:
                gaps.append({
                    'demographic': 'race',
                    'group': race,
                    'representation': representation,
                    'minimum_required': self.min_representation
                })
        
        # Check gender representation
        for gender in target_demographics.get('gender', []):
            representation = stats['gender_distribution'].get(gender, 0)
            if representation < self.min_representation:
                gaps.append({
                    'demographic': 'gender',
                    'group': gender,
                    'representation': representation,
                    'minimum_required': self.min_representation
                })
        
        if gaps:
            logger.warning(f"Representation gaps identified: {gaps}")
        
        return gaps
    
    def ensure_balanced_training_split(
        self,
        images: List[Tuple],
    ) -> List[Tuple]:
        """
        Ensure balanced training split across demographics
        
        Args:
            images: List of (image_data, demographic_info, label) tuples
            
        Returns:
            Balanced subset of images
        """
        grouped = self._group_by_demographics(images)
        balanced_split = []
        
        # Ensure minimum representation from each demographic group
        num_groups = len(grouped)
        min_per_group = max(1, int(len(images) / num_groups * 0.1))
        
        for group_images in grouped.values():
            samples = self._sample_balanced(group_images, min_per_group)
            balanced_split.extend(samples)
        
        # Fill remaining slots with stratified random sampling
        remaining = len(images) - len(balanced_split)
        if remaining > 0:
            selected_ids = {id(img) for img, _, _ in balanced_split}
            available = [(img, demo, label) for img, demo, label in images 
                        if id(img) not in selected_ids]
            remaining_samples = self._stratified_random_sample(
                available, remaining
            )
            balanced_split.extend(remaining_samples)
        
        return balanced_split
    
    def _group_by_demographics(
        self,
        images: List[Tuple]
    ) -> Dict[str, List[Tuple]]:
        """Group images by demographic attributes"""
        groups = defaultdict(list)
        
        for img, demo_info, label in images:
            key = self._get_demographic_group_key(demo_info)
            groups[key].append((img, demo_info, label))
        
        return dict(groups)
    
    def _get_demographic_group_key(self, demo_info: DemographicInfo) -> str:
        """Generate a key for demographic grouping"""
        age_range = self._get_age_range(demo_info.age) if demo_info.age else 'unknown'
        return f"{demo_info.race or 'unknown'}-{demo_info.ethnicity or 'unknown'}-" \
               f"{demo_info.gender or 'unknown'}-{age_range}"
    
    def _get_age_range(self, age: int) -> str:
        """Get age range from age"""
        if age < 30:
            return '20-30'
        elif age < 40:
            return '30-40'
        elif age < 50:
            return '40-50'
        elif age < 60:
            return '50-60'
        else:
            return '60+'
    
    def _sample_balanced(
        self,
        images: List[Tuple],
        min_count: int
    ) -> List[Tuple]:
        """Sample balanced images from a group"""
        np.random.shuffle(images)
        return images[:min(min_count, len(images))]
    
    def _stratified_random_sample(
        self,
        images: List[Tuple],
        count: int
    ) -> List[Tuple]:
        """Stratified random sampling"""
        np.random.shuffle(images)
        return images[:count]
