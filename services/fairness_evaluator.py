"""
Fairness Evaluator Service for RetinaScan AI Backend
Provides bias detection and fairness metrics calculation
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class FairnessMetrics:
    """Fairness metrics for model evaluation"""
    accuracy: float
    sensitivity: float
    specificity: float
    false_positive_rate: float
    false_negative_rate: float
    demographic_parity: float
    equalized_odds: float
    predictive_parity: float


@dataclass
class BiasFlag:
    """Represents a detected bias issue"""
    severity: str  # 'low', 'medium', 'high'
    metric: str
    subgroup: str
    value: float
    threshold: float
    description: str


class FairnessEvaluator:
    """
    Evaluates model fairness across demographic groups
    """
    
    def __init__(self):
        self.fairness_thresholds = {
            'demographic_parity': 0.8,
            'equalized_odds': 0.85,
            'false_positive_parity': 0.8,
            'false_negative_parity': 0.8,
            'accuracy_disparity': 0.15,
        }
    
    def calculate_fairness_metrics(
        self,
        predictions: np.ndarray,
        labels: np.ndarray,
        demographic_groups: Dict[str, np.ndarray]
    ) -> Dict[str, FairnessMetrics]:
        """
        Calculate fairness metrics for overall and each demographic group
        
        Args:
            predictions: Model predictions (0-4 severity levels)
            labels: True labels
            demographic_groups: Dictionary mapping group names to boolean masks
            
        Returns:
            Dictionary of group name to FairnessMetrics
        """
        metrics = {}
        
        # Overall metrics
        metrics['overall'] = self._calculate_group_metrics(
            predictions, labels, np.ones_like(predictions, dtype=bool)
        )
        
        # Subgroup metrics
        for group_name, group_mask in demographic_groups.items():
            if np.sum(group_mask) > 0:
                metrics[group_name] = self._calculate_group_metrics(
                    predictions, labels, group_mask
                )
        
        return metrics
    
    def _calculate_group_metrics(
        self,
        predictions: np.ndarray,
        labels: np.ndarray,
        group_mask: np.ndarray
    ) -> FairnessMetrics:
        """Calculate metrics for a specific group"""
        
        # Filter to group
        group_preds = predictions[group_mask]
        group_labels = labels[group_mask]
        
        if len(group_preds) == 0:
            return FairnessMetrics(
                accuracy=0.0,
                sensitivity=0.0,
                specificity=0.0,
                false_positive_rate=0.0,
                false_negative_rate=0.0,
                demographic_parity=0.0,
                equalized_odds=0.0,
                predictive_parity=0.0,
            )
        
        # Convert to binary: 0 = No DR, >0 = DR present
        binary_preds = (group_preds > 0).astype(int)
        binary_labels = (group_labels > 0).astype(int)
        
        # Calculate confusion matrix components
        tp = np.sum((binary_preds == 1) & (binary_labels == 1))
        tn = np.sum((binary_preds == 0) & (binary_labels == 0))
        fp = np.sum((binary_preds == 1) & (binary_labels == 0))
        fn = np.sum((binary_preds == 0) & (binary_labels == 1))
        
        # Calculate metrics
        total = len(group_preds)
        accuracy = (tp + tn) / total if total > 0 else 0.0
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        false_negative_rate = fn / (fn + tp) if (fn + tp) > 0 else 0.0
        
        # Demographic parity: proportion of positive predictions
        demographic_parity = np.mean(binary_preds)
        
        # Equalized odds: similarity of TPR and FPR across groups
        # (calculated at higher level)
        equalized_odds = 1.0 - abs(sensitivity - (1 - specificity))
        
        # Predictive parity: P(Y=1|Y_hat=1) = PPV
        predictive_parity = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        
        return FairnessMetrics(
            accuracy=float(accuracy),
            sensitivity=float(sensitivity),
            specificity=float(specificity),
            false_positive_rate=float(false_positive_rate),
            false_negative_rate=float(false_negative_rate),
            demographic_parity=float(demographic_parity),
            equalized_odds=float(equalized_odds),
            predictive_parity=float(predictive_parity),
        )
    
    def detect_bias_flags(
        self,
        metrics: Dict[str, FairnessMetrics]
    ) -> List[BiasFlag]:
        """
        Detect bias issues from fairness metrics
        
        Args:
            metrics: Dictionary of group metrics
            
        Returns:
            List of detected bias flags
        """
        flags = []
        overall_metrics = metrics.get('overall')
        
        if overall_metrics is None:
            return flags
        
        for group_name, group_metrics in metrics.items():
            if group_name == 'overall':
                continue
            
            # Check demographic parity
            parity_diff = abs(
                group_metrics.demographic_parity - overall_metrics.demographic_parity
            )
            if parity_diff > (1 - self.fairness_thresholds['demographic_parity']):
                flags.append(BiasFlag(
                    severity='high',
                    metric='demographic_parity',
                    subgroup=group_name,
                    value=group_metrics.demographic_parity,
                    threshold=self.fairness_thresholds['demographic_parity'],
                    description=f'Significant demographic parity bias for {group_name}'
                ))
            
            # Check equalized odds
            if group_metrics.equalized_odds < self.fairness_thresholds['equalized_odds']:
                flags.append(BiasFlag(
                    severity='medium',
                    metric='equalized_odds',
                    subgroup=group_name,
                    value=group_metrics.equalized_odds,
                    threshold=self.fairness_thresholds['equalized_odds'],
                    description=f'Unequal true positive rates for {group_name}'
                ))
            
            # Check false positive rate
            if group_metrics.false_positive_rate > (
                1 - self.fairness_thresholds['false_positive_parity']
            ):
                flags.append(BiasFlag(
                    severity='high',
                    metric='false_positive_rate',
                    subgroup=group_name,
                    value=group_metrics.false_positive_rate,
                    threshold=1 - self.fairness_thresholds['false_positive_parity'],
                    description=f'High false positive rate for {group_name} may lead to over-referral'
                ))
            
            # Check false negative rate
            if group_metrics.false_negative_rate > (
                1 - self.fairness_thresholds['false_negative_parity']
            ):
                flags.append(BiasFlag(
                    severity='high',
                    metric='false_negative_rate',
                    subgroup=group_name,
                    value=group_metrics.false_negative_rate,
                    threshold=1 - self.fairness_thresholds['false_negative_parity'],
                    description=f'High false negative rate for {group_name} may lead to missed diagnoses'
                ))
            
            # Check accuracy disparity
            accuracy_diff = abs(group_metrics.accuracy - overall_metrics.accuracy)
            if accuracy_diff > self.fairness_thresholds['accuracy_disparity']:
                flags.append(BiasFlag(
                    severity='medium',
                    metric='accuracy_disparity',
                    subgroup=group_name,
                    value=accuracy_diff,
                    threshold=self.fairness_thresholds['accuracy_disparity'],
                    description=f'Significant accuracy disparity for {group_name}'
                ))
        
        return flags
    
    def generate_recommendations(
        self,
        metrics: Dict[str, FairnessMetrics],
        flags: List[BiasFlag]
    ) -> List[str]:
        """Generate actionable recommendations based on audit"""
        recommendations = []
        
        high_severity_flags = [f for f in flags if f.severity == 'high']
        if high_severity_flags:
            recommendations.append(
                'Immediate model retraining required with focus on underrepresented groups'
            )
            recommendations.append(
                'Consider collecting additional data for affected demographic groups'
            )
        
        racial_biases = [f for f in flags if 'race' in f.subgroup.lower() or 'ethnicity' in f.subgroup.lower()]
        if len(racial_biases) > 2:
            recommendations.append(
                'Implement racial bias mitigation techniques: adversarial debiasing and reweighting'
            )
            recommendations.append(
                'Engage with diverse clinical partners for dataset validation'
            )
        
        # Accuracy disparity recommendations
        if 'overall' in metrics:
            overall = metrics['overall']
            accuracies = [m.accuracy for m in metrics.values()]
            if len(accuracies) > 1:
                accuracy_disparity = max(accuracies) - min(accuracies)
                if accuracy_disparity > self.fairness_thresholds['accuracy_disparity']:
                    recommendations.append(
                        'Significant accuracy disparities detected. Implement subgroup-specific calibration'
                    )
        
        if overall.false_negative_rate > 0.2:
            recommendations.append(
                'Overall false negative rate is high. Adjust sensitivity thresholds'
            )
        
        if overall.false_positive_rate > 0.3:
            recommendations.append(
                'Overall false positive rate is high. Consider stricter specificity requirements'
            )
        
        return recommendations
    
    def perform_comprehensive_audit(
        self,
        predictions: np.ndarray,
        labels: np.ndarray,
        demographic_groups: Dict[str, np.ndarray]
    ) -> Dict:
        """
        Perform comprehensive fairness audit
        
        Returns:
            Dictionary containing metrics, flags, and recommendations
        """
        metrics = self.calculate_fairness_metrics(
            predictions, labels, demographic_groups
        )
        
        flags = self.detect_bias_flags(metrics)
        
        recommendations = self.generate_recommendations(metrics, flags)
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': {
                k: {
                    'accuracy': m.accuracy,
                    'sensitivity': m.sensitivity,
                    'specificity': m.specificity,
                    'false_positive_rate': m.false_positive_rate,
                    'false_negative_rate': m.false_negative_rate,
                    'demographic_parity': m.demographic_parity,
                    'equalized_odds': m.equalized_odds,
                    'predictive_parity': m.predictive_parity,
                }
                for k, m in metrics.items()
            },
            'bias_flags': [
                {
                    'severity': f.severity,
                    'metric': f.metric,
                    'subgroup': f.subgroup,
                    'value': f.value,
                    'threshold': f.threshold,
                    'description': f.description,
                }
                for f in flags
            ],
            'recommendations': recommendations,
        }
