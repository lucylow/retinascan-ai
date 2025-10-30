from datetime import datetime
from typing import Any, Dict, List

import numpy as np

from xai_engine import XAIEngine, ExplanationResult


class TransparencyAgent:
    """Agent responsible for ensuring AI transparency and explainability"""

    def __init__(self, model):
        self.xai_engine = XAIEngine(model)
        self.explanation_history = []
        self.audit_log = []

    def generate_comprehensive_explanation(self, workflow_data: Dict) -> Dict:
        """Generate comprehensive explanation for entire workflow"""

        image_data = workflow_data.get('image_data')
        prediction = workflow_data.get('prediction_result', {})
        patient_context = workflow_data.get('metadata', {})

        explanation = self.xai_engine.generate_explanation(
            image=image_data,
            prediction=prediction,
            original_image=image_data,
            patient_context=patient_context
        )

        patient_explanation = self.xai_engine.generate_patient_explanation(explanation)

        transparency_report = {
            'technical_explanation': self._format_technical_explanation(explanation),
            'patient_explanation': patient_explanation,
            'clinical_evidence': explanation.clinical_evidence,
            'uncertainty_analysis': explanation.uncertainty_metrics,
            'alternative_diagnoses': explanation.alternative_diagnoses,
            'decision_audit_trail': self._create_audit_trail(workflow_data, explanation),
            'quality_metrics': self._calculate_explanation_quality(explanation),
            'timestamp': datetime.now().isoformat()
        }

        self._log_explanation(workflow_data.get('workflow_id', 'unknown'), transparency_report)

        return transparency_report

    def _format_technical_explanation(self, explanation: ExplanationResult) -> Dict:
        """Format technical explanation for clinicians"""

        return {
            'decision_summary': {
                'primary_diagnosis': next(
                    (f['value'] for f in explanation.decision_factors
                     if f['factor'] == 'Primary Diagnosis'), 'Unknown'),
                'confidence': explanation.confidence_scores,
                'key_factors': [
                    {
                        'factor': factor['factor'],
                        'influence': factor['influence'],
                        'reasoning': factor['explanation']
                    }
                    for factor in explanation.decision_factors
                    if factor['factor'] != 'Primary Diagnosis'
                ]
            },
            'feature_analysis': {
                'most_important_features': [
                    {'feature': feat, 'importance': score}
                    for feat, score in sorted(
                        explanation.feature_importance.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:3]
                ],
                'heatmap_visualization': explanation.heatmap_data
            },
            'uncertainty_breakdown': {
                'level': explanation.uncertainty_metrics['uncertainty_level'],
                'entropy': explanation.uncertainty_metrics['prediction_entropy'],
                'confidence_gap': explanation.uncertainty_metrics['confidence_gap'],
                'interpretation': self._interpret_uncertainty(explanation.uncertainty_metrics)
            }
        }

    def _interpret_uncertainty(self, uncertainty_metrics: Dict) -> str:
        """Interpret uncertainty metrics for clinicians"""

        level = uncertainty_metrics['uncertainty_level']
        if level == 'Low':
            return "High confidence in diagnosis. AI decision is reliable."
        elif level == 'Medium':
            return "Moderate uncertainty. Consider clinical context and human review."
        else:
            return "High uncertainty. Strongly recommend expert review and additional testing."

    def _create_audit_trail(self, workflow_data: Dict, explanation: ExplanationResult) -> List[Dict]:
        """Create comprehensive audit trail of decision process"""

        audit_entries = []

        audit_entries.append({
            'timestamp': workflow_data.get('timestamp', datetime.now().isoformat()),
            'stage': 'Image Processing',
            'action': 'Image quality assessment completed',
            'details': f"Quality score: {workflow_data.get('quality_score', 'N/A')}",
            'agent': 'DataProcessorAgent'
        })

        audit_entries.append({
            'timestamp': datetime.now().isoformat(),
            'stage': 'AI Analysis',
            'action': 'Deep learning model prediction generated',
            'details': f"Diagnosis: {explanation.decision_factors[0]['value']}",
            'agent': 'ModelSpecialistAgent'
        })

        audit_entries.append({
            'timestamp': datetime.now().isoformat(),
            'stage': 'Transparency',
            'action': 'Explainable AI analysis completed',
            'details': f"Uncertainty: {explanation.uncertainty_metrics['uncertainty_level']}",
            'agent': 'TransparencyAgent'
        })

        top_feature = max(explanation.feature_importance.items(), key=lambda x: x[1])
        audit_entries.append({
            'timestamp': datetime.now().isoformat(),
            'stage': 'Feature Analysis',
            'action': 'Key contributing features identified',
            'details': f"Most important feature: {top_feature[0]} (score: {top_feature[1]:.2f})",
            'agent': 'XAIEngine'
        })

        return audit_entries

    def _calculate_explanation_quality(self, explanation: ExplanationResult) -> Dict:
        """Calculate quality metrics for the explanation"""

        feature_scores = list(explanation.feature_importance.values())
        feature_clarity = float(np.std(feature_scores))
        factor_completeness = min(len(explanation.decision_factors) / 5, 1.0)
        uncertainty_transparency = 1.0 if explanation.uncertainty_metrics['uncertainty_level'] != 'Unknown' else 0.5

        quality_score = (
            feature_clarity * 0.4 +
            factor_completeness * 0.3 +
            uncertainty_transparency * 0.3
        )

        return {
            'overall_score': float(quality_score),
            'feature_clarity': float(feature_clarity),
            'factor_completeness': float(factor_completeness),
            'uncertainty_transparency': float(uncertainty_transparency),
            'interpretation': self._interpret_quality_score(quality_score)
        }

    def _interpret_quality_score(self, score: float) -> str:
        """Interpret explanation quality score"""

        if score >= 0.8:
            return "High quality explanation - comprehensive and clear"
        elif score >= 0.6:
            return "Good quality explanation - adequate for clinical use"
        elif score >= 0.4:
            return "Moderate quality - some aspects could be clearer"
        else:
            return "Low quality - limited explanatory value"

    def _log_explanation(self, workflow_id: str, report: Dict):
        """Log explanation for audit purposes"""

        log_entry = {
            'workflow_id': workflow_id,
            'timestamp': datetime.now().isoformat(),
            'diagnosis': report['technical_explanation']['decision_summary']['primary_diagnosis'],
            'explanation_quality': report['quality_metrics']['overall_score'],
            'uncertainty_level': report['technical_explanation']['uncertainty_breakdown']['level'],
            'key_factors_count': len(report['technical_explanation']['decision_summary']['key_factors'])
        }

        self.explanation_history.append(log_entry)

        if len(self.explanation_history) > 1000:
            self.explanation_history = self.explanation_history[-1000:]

    def generate_explanation_dashboard(self, workflow_id: str) -> Dict:
        """Generate dashboard data for explanation visualization"""

        explanation_record = next(
            (exp for exp in self.explanation_history if exp['workflow_id'] == workflow_id),
            None
        )

        if not explanation_record:
            return {'error': 'Explanation not found'}

        return {
            'workflow_id': workflow_id,
            'explanation_metrics': explanation_record,
            'historical_comparison': self._get_historical_comparison(explanation_record),
            'quality_trends': self._get_quality_trends(),
            'common_patterns': self._identify_common_patterns()
        }

    def _get_historical_comparison(self, current_explanation: Dict) -> Dict:
        """Compare current explanation with historical patterns"""

        similar_cases = [
            exp for exp in self.explanation_history
            if exp['diagnosis'] == current_explanation['diagnosis']
            and exp['workflow_id'] != current_explanation['workflow_id']
        ]

        if not similar_cases:
            return {'message': 'No similar historical cases for comparison'}

        avg_quality = float(np.mean([case['explanation_quality'] for case in similar_cases]))
        avg_factors = float(np.mean([case['key_factors_count'] for case in similar_cases]))

        return {
            'similar_cases_count': len(similar_cases),
            'quality_comparison': {
                'current': current_explanation['explanation_quality'],
                'average_similar_cases': avg_quality,
                'difference': current_explanation['explanation_quality'] - avg_quality
            },
            'factors_comparison': {
                'current': current_explanation['key_factors_count'],
                'average_similar_cases': avg_factors,
                'difference': current_explanation['key_factors_count'] - avg_factors
            }
        }

    def _get_quality_trends(self) -> Dict:
        """Get trends in explanation quality over time"""

        if len(self.explanation_history) < 10:
            return {'message': 'Insufficient data for trend analysis'}

        recent_explanations = self.explanation_history[-50:]
        quality_scores = [exp['explanation_quality'] for exp in recent_explanations]

        return {
            'trend_period': 'Last 50 cases',
            'average_quality': float(np.mean(quality_scores)),
            'quality_std': float(np.std(quality_scores)),
            'trend_direction': 'improving' if quality_scores[-1] > quality_scores[0] else 'declining',
            'min_quality': float(min(quality_scores)),
            'max_quality': float(max(quality_scores))
        }

    def _identify_common_patterns(self) -> List[Dict]:
        """Identify common patterns in explanations"""

        if len(self.explanation_history) < 20:
            return [{'message': 'Insufficient data for pattern analysis'}]

        diagnosis_groups = {}
        for exp in self.explanation_history:
            diagnosis = exp['diagnosis']
            if diagnosis not in diagnosis_groups:
                diagnosis_groups[diagnosis] = []
            diagnosis_groups[diagnosis].append(exp)

        patterns = []
        for diagnosis, cases in diagnosis_groups.items():
            if len(cases) >= 5:
                avg_quality = float(np.mean([case['explanation_quality'] for case in cases]))
                patterns.append({
                    'diagnosis': diagnosis,
                    'case_count': len(cases),
                    'average_explanation_quality': avg_quality,
                    'quality_consistency': 'High' if np.std([case['explanation_quality'] for case in cases]) < 0.2 else 'Medium'
                })

        return sorted(patterns, key=lambda x: x['case_count'], reverse=True)[:5]


